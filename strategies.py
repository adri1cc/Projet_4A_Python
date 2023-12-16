import os

import api
import logging
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tqdm import tqdm

class BaseStrategy:
    def __init__(self, pair, timeframe):
        """
        Initialize a BaseStrategy object.

        :param pair: Trading pair (e.g., 'BTC/USD').
        :param timeframe: Timeframe for analysis (e.g., '1h').
        """
        self._pair = pair
        self._timeframe = timeframe
        self._df = None
        self._live_trade = False
        self._portfolio_values = []
        self._last_portfolio_value = 1000

    def set_live_trade(self, side):
        """
        Set the live trade status.

        :param side: Boolean indicating the live trade status.
        """
        self._live_trade = side

    def get_live_trade(self):
        """
        Get the live trade status.

        :return: Boolean indicating the live trade status.
        """
        return self._live_trade

    def prepare_backtest_data(self, since):
        """
        Generate the path for saving backtest data.

        :param since: Start date for backtesting.
        :return: Path to store backtest data.
        """
        pair_dir = self._pair.replace('/', '_')
        output_dir = f"{pair_dir}_data"
        formatted_since = since.replace(':', '-').replace(' ', '_')
        filename = f"{pair_dir}_{self._timeframe}_{formatted_since}.csv"
        path = os.path.join(output_dir, filename)
        return path
    
    def load_data(self, path, since):
        """
        Load historical data for backtesting.

        :param path: Path to historical data file.
        :param since: Start date for loading data.
        :return: DataFrame containing historical data.
        """
        if not os.path.exists(path):
            logging.info("Need to download data...")
            historical_data = api.get_historical_data(self._pair, self._timeframe, since)
            historical_data = pd.read_csv(path)
        else:
            logging.info("Using existing data...")
            historical_data = pd.read_csv(path)
        return historical_data
    
    def plot_figure(self):
        """
        Plot a figure showing candlestick chart, portfolio values, and portfolio changes.

        :return: Plotly figure object.
        """
        sell, prix, portfolio_values, changes = zip(*self._portfolio_values)
        dates = self._df.index

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
        # fig.add_trace(go.Candlestick(x=dates,
        #                  open=self._df['Open'],
        #                  high=self._df['High'],
        #                  low=self._df['Low'],
        #                  close=self._df['Close'],
        #                  name=f'{self._pair} Candlestick'),
        #   row=1, col=1)
        fig.add_trace(go.Scatter(x=dates, y=self._df['Close'], mode='lines', name=f"Values of {self._pair}"), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell, y=portfolio_values, mode='lines', name='Portfolio Values'), row=2, col=1)
        fig.add_trace(go.Bar(x=sell, y=changes, name='Portfolio Changes'), row=3, col=1)
        title = 'Backtest ' + self._pair
        fig.update_layout(title_text=title, showlegend=True)
        fig.update_layout(xaxis_rangeslider_visible=False)
        return fig

    def is_data_empty(self):
        """
        Check if historical data is empty.

        :return: True if data is empty, False otherwise.
        """
        if self._df is None or len(self._df) == 0:
            logging.warning("DataFrame is empty or None.")
            return True
        return False

    def set_data(self, data):
        """
        Set historical data for the strategy.

        :param data: DataFrame containing historical data.
        """
        self._df = data

    def get_data(self):
        """
        Get historical data for the strategy.

        :return: DataFrame containing historical data.
        """
        return self._df

    def set_last_portfolio_value(self, value):
        """
        Set the last portfolio value.

        :param value: The last portfolio value.
        """
        self._last_portfolio_value = value

    def get_last_portfolio_value(self):
        """
        Get the last portfolio value.

        :return: The last portfolio value.
        """
        return self._last_portfolio_value

    def __del__(self):
        """
        Destructor method.
        """
        return


class SimpleSMALive(BaseStrategy):
    def __init__(self, pair, timeframe, sma):
        """
        Initialize SimpleSMALive object.

        :param pair: Trading pair (e.g., 'BTC/USD').
        :param timeframe: Timeframe for analysis (e.g., '1h').
        :param sma: Simple Moving Average parameter.
        """
        super().__init__(pair, timeframe)
        self.__sma = sma

    def update_data(self):
        """
        Update historical data for SMA calculation.
        """
        if self._df is None:
            self._df = api.get_ohlcv(self._pair, self._timeframe, limit=self.__sma + 1)
        new_data = api.get_ohlcv(self._pair, self._timeframe, limit=1)
        self._df = pd.concat([self._df, new_data], ignore_index=True)
        self._df = self._df.drop_duplicates(subset=['Timestamp'], keep='last')


    def backtest(self, since):
        """
        Perform a backtest using the Simple Moving Average (SMA) strategy.

        :param since: Start date for the backtest.
        """
        # Utilize inherited methods and attributes
        logging.info("Calculating backtest ...")
        if since is None:
            since = '2023-06-11 00:00:00'

        self.set_live_trade(False)
        self._portfolio_values = []

        path = self.prepare_backtest_data(since)
        historical_data = super().load_data(path, since)
        super().set_data(historical_data.copy())

        initial_portfolio_value = 1000
        super().set_last_portfolio_value(initial_portfolio_value)
        logging.info(f"Initial Portfolio Value: {initial_portfolio_value}")

        close_prices = super().get_data()['Close']
        timestamps = super().get_data()['Timestamp']

        super().get_data()['SMA'] = close_prices.rolling(self.__sma).mean()

        for i in tqdm(range(self.__sma, len(super().get_data())), desc="Backtesting Progress"):
            close_price = close_prices.iloc[i]
            timestamp = timestamps.iloc[i]

            last_sma = super().get_data()['SMA'].iloc[i - 1]
            signal = "buy" if close_price > last_sma else "sell" if close_price < last_sma else 0

            if signal == "buy" and not self.get_live_trade():
                self.set_live_trade(True)
                prix_achat = close_price
                logging.info(f"Buy Signal: {timestamp}, Price: {prix_achat}")

            elif signal == "sell" and self.get_live_trade():
                self.set_live_trade(False)
                difference_de_prix = close_price - prix_achat
                valeur_apres_vente = super().get_last_portfolio_value() + \
                                     super().get_last_portfolio_value() * difference_de_prix / prix_achat
                super().set_last_portfolio_value(valeur_apres_vente)
                self._portfolio_values.append(
                    (timestamp, round(prix_achat, 2), round(super().get_last_portfolio_value(), 2),
                     round(difference_de_prix, 2)))
                logging.info(f"Sell Signal: {timestamp}, Price: {close_price}, Portfolio Value: {round(valeur_apres_vente, 2)}")

        logging.info("Backtest complete. Performance metrics:")
        logging.info(f"Initial Portfolio Value: {initial_portfolio_value}")
        logging.info(f"Final Portfolio Value: {round(super().get_last_portfolio_value(), 2)}")
        logging.info(f"Portfolio Return: {100 * (super().get_last_portfolio_value() / initial_portfolio_value - 1):.2f}%")
        return

    # Override or add other methods as needed...

    def calculate_signal(self):
        """
        Calculate SMA signal based on the current data.

        :return: Buy, sell, or hold signal.
        """
        self.update_data()
        if super().is_data_empty():
            return 0

        self.calculate_sma()
        signal = self.generate_signal()
        return signal

    def calculate_sma(self):
        """
        Calculate SMA values and add them to the DataFrame.
        """
        self._df['SMA'] = self._df['Close'].rolling(self.__sma).mean()

    def generate_signal(self):
        """
        Generate buy, sell, or hold signal based on SMA values.

        :return: Buy, sell, or hold signal.
        """
        last_value = self._df['Close'].iloc[-1]
        last_sma = self._df['SMA'].iloc[-2]

        if pd.isnull(last_sma):
            return 0

        if last_value > last_sma:
            return "buy"
        elif last_value < last_sma:
            return "sell"

        return 0

class RSIStrategy(BaseStrategy): #TODO Finish and verify it
    def __init__(self, pair, timeframe, rsi_period, overbought_threshold=70, oversold_threshold=30):
        """
        Initialize RSIStrategy object.

        :param pair: Trading pair (e.g., 'BTC/USD').
        :param timeframe: Timeframe for analysis (e.g., '1h').
        :param rsi_period: RSI period for calculation.
        :param overbought_threshold: Overbought threshold for RSI (default is 70).
        :param oversold_threshold: Oversold threshold for RSI (default is 30).
        """
        super().__init__(pair, timeframe)
        self.__rsi_period = rsi_period
        self.__overbought_threshold = overbought_threshold
        self.__oversold_threshold = oversold_threshold

    def update_data(self):
        """
        Update historical data for RSI calculation.
        """
        if self._df is None:
            self._df = api.get_ohlcv(self._pair, self._timeframe, limit=self.__rsi_period + 1)
        new_data = api.get_ohlcv(self._pair, self._timeframe, limit=1)
        self._df = pd.concat([self._df, new_data], ignore_index=True)
        self._df = self._df.drop_duplicates(subset=['Timestamp'], keep='last')

    def backtest(self, since):
        """
        Perform a backtest using the Relative Strength Index (RSI) strategy.

        :param since: Start date for the backtest.
        """
        # Utilize inherited methods and attributes
        logging.info("Calculating backtest ...")
        if since is None:
            since = '2023-06-11 00:00:00'

        self.set_live_trade(False)
        self._portfolio_values = []

        path = self.prepare_backtest_data(since)
        historical_data = super().load_data(path, since)
        super().set_data(historical_data.copy())

        initial_portfolio_value = 1000
        super().set_last_portfolio_value(initial_portfolio_value)
        logging.info(f"Initial Portfolio Value: {initial_portfolio_value}")

        close_prices = super().get_data()['Close']
        timestamps = super().get_data()['Timestamp']

        super().get_data()['RSI'] = self.calculate_rsi(close_prices)

        for i in tqdm(range(self.__rsi_period, len(super().get_data())), desc="Backtesting Progress"):
            close_price = close_prices.iloc[i]
            timestamp = timestamps.iloc[i]

            last_rsi = super().get_data()['RSI'].iloc[i - 1]
            signal = self.generate_signal(last_rsi)

            if signal == "buy" and not self.get_live_trade():
                self.set_live_trade(True)
                prix_achat = close_price
                logging.info(f"Buy Signal: {timestamp}, Price: {prix_achat}")

            elif signal == "sell" and self.get_live_trade():
                self.set_live_trade(False)
                difference_de_prix = close_price - prix_achat
                valeur_apres_vente = super().get_last_portfolio_value() + \
                                     super().get_last_portfolio_value() * difference_de_prix / prix_achat
                super().set_last_portfolio_value(valeur_apres_vente)
                self._portfolio_values.append(
                    (timestamp, round(prix_achat, 2), round(super().get_last_portfolio_value(), 2),
                     round(difference_de_prix, 2)))
                logging.info(
                    f"Sell Signal: {timestamp}, Price: {close_price}, Portfolio Value: {round(valeur_apres_vente, 2)}")

        logging.info("Backtest complete. Performance metrics:")
        logging.info(f"Initial Portfolio Value: {initial_portfolio_value}")
        logging.info(f"Final Portfolio Value: {round(super().get_last_portfolio_value(), 2)}")
        logging.info(f"Portfolio Return: {100 * (super().get_last_portfolio_value() / initial_portfolio_value - 1):.2f}")
        return

    # Override or add other methods as needed...

    def calculate_rsi(self, close_prices):
        """
        Calculate RSI values and add them to the DataFrame.

        :param close_prices: Series containing closing prices.
        """
        daily_returns = close_prices.diff().dropna()
        gain = daily_returns[daily_returns > 0].mean()
        loss = -daily_returns[daily_returns < 0].mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return pd.concat([pd.Series([None] * (self.__rsi_period - 1)), rsi], ignore_index=True)

    def generate_signal(self, rsi_value):
        """
        Generate buy, sell, or hold signal based on RSI values.

        :param rsi_value: Current RSI value.
        :return: Buy, sell, or hold signal.
        """
        if pd.isnull(rsi_value):
            return 0

        if rsi_value > self.__overbought_threshold:
            return "sell"
        elif rsi_value < self.__oversold_threshold:
            return "buy"

        return 0
