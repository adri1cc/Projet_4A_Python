"""
This script contains the code of the differents strategies.
"""
import os
import api
import logging
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tqdm import tqdm

import api

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
    
    def is_data_empty(self):
        """
        Check if historical data is empty.

        :return: True if data is empty, False otherwise.
        """
        if self._df is None or len(self._df) == 0:
            logging.warning("DataFrame is empty or None.")
            return True
        return False
    
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
        fig.add_trace(go.Scatter(x=dates, y=self._df['Close'], mode='lines', name=f"Values of {self._pair}"), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell, y=portfolio_values, mode='lines', name='Portfolio Values'), row=2, col=1)
        fig.add_trace(go.Bar(x=sell, y=changes, name='Portfolio Changes'), row=3, col=1)
        title = 'Backtest ' + self._pair
        fig.update_layout(title_text=title, showlegend=True)
        fig.update_layout(xaxis_rangeslider_visible=False)
        return fig

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
            #print(last_sma)
            signal = "buy" if close_price > last_sma else "sell" if close_price < last_sma else 0

            if signal == "buy" and not self.get_live_trade():
                self.set_live_trade(True)
                prix_achat = close_price
                logging.info(f"Buy Signal: {timestamp}, Price: {prix_achat}")

            elif signal == "sell" and self.get_live_trade():
                self.set_live_trade(False)
                difference_de_prix = close_price - prix_achat

                valeur_apres_vente = super().get_last_portfolio_value() + \
                     super().get_last_portfolio_value() * (difference_de_prix / prix_achat)

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

class RSIStrategy(BaseStrategy): #TODO La rendre fonctionnelle "ValueError pour portfolio_values: not enough values to unpack (expected 4, got 0)"
    def __init__(self, pair, timeframe, rsi_period=14):
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
        self.__overbought_threshold = 70
        self.__oversold_threshold = 30

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
        #print(close_prices)

        super().get_data()['RSI'] = self.calculate_rsi(close_prices)

        for i in tqdm(range(self.__rsi_period, len(super().get_data())), desc="Backtesting Progress"):
            close_price = close_prices.iloc[i]
            timestamp = timestamps.iloc[i]

            last_rsi = super().get_data()['RSI'].iloc[i - 1]

            #signal = self.generate_signal(last_rsi)
            signal = "buy" if last_rsi < self.__oversold_threshold else "sell" if last_rsi > self.__overbought_threshold else 0

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

            elif signal == "0":
                print("0")

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
        # Extract the 'Close' column if close_prices is a DataFrame
        #close_prices = close_prices['Close'] if isinstance(close_prices, pd.DataFrame) else close_prices

        daily_returns = close_prices.diff().dropna()
        #print(daily_returns)
        
        # Calculate gain and loss with positive and negative values
        #gain = daily_returns[daily_returns > 0].rolling(self.__rsi_period).mean()
        gain = daily_returns.apply(lambda x: x if x>0 else 0)
        #print(gain) 
        #loss = -daily_returns[daily_returns < 0].rolling(self.__rsi_period).mean()
        loss = daily_returns.apply(lambda x: -x if x<0 else 0)
        #print(loss) 

        # Handling division by zero
        if loss.empty or (loss == 0).all():
            return pd.Series([100.0] * len(close_prices), index=close_prices.index)

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        #print(rsi)

        # Create a new Series with None values and the appropriate index
        none_values = pd.Series([None] * (self.__rsi_period - 1), index=range(self.__rsi_period - 1))

        # Concatenate the None values and the calculated RSI values
        if isinstance(rsi, pd.Series):
            return pd.concat([none_values, rsi], ignore_index=True)
        else:
            # If rsi is a scalar, create a Series with the same index and fill it with the scalar value
            return pd.Series([rsi] * len(close_prices), index=close_prices.index)


    def generate_signal(self):
        """
        Generate buy, sell, or hold signal based on RSI values.

        :return: Buy, sell, or hold signal.
        """
        if super().is_data_empty():
            return 0

        last_rsi = super().get_data()['RSI'].iloc[-1]

        if pd.isnull(last_rsi):
            return 0

        if last_rsi > self.__overbought_threshold:
            return "sell"  # sell here
        elif last_rsi < self.__oversold_threshold:
            return "buy"  # buy

        return 0

class MACDLive(BaseStrategy):
    def __init__(self, pair, timeframe, short_window=12, long_window=26, signal_window=9):
        """
        Initialize MACDLive object.

        :param pair: Trading pair (e.g., 'BTC/USD').
        :param timeframe: Timeframe for analysis (e.g., '1h').
        :param short_window: Short window for MACD calculation.
        :param long_window: Long window for MACD calculation.
        :param signal_window: Signal window for MACD calculation.
        """
        super().__init__(pair, timeframe)
        self.__short_window = short_window
        self.__long_window = long_window
        self.__signal_window = signal_window

    def update_data(self):
        """
        Update historical data for MACD calculation.
        """
        if self._df is None:
            self._df = api.get_ohlcv(self._pair, self._timeframe, limit=self.__long_window + self.__signal_window)
        new_data = api.get_ohlcv(self._pair, self._timeframe, limit=1)
        self._df = pd.concat([self._df, new_data], ignore_index=True)
        self._df = self._df.drop_duplicates(subset=['Timestamp'], keep='last')

    def backtest(self, since):
        """
        Perform a backtest using the Moving Average Convergence Divergence (MACD) strategy.

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

        super().get_data()['Short_MA'] = close_prices.rolling(self.__short_window).mean()
        super().get_data()['Long_MA'] = close_prices.rolling(self.__long_window).mean()

        super().get_data()['MACD'] = self.calculate_macd(close_prices)

        for i in tqdm(range(self.__long_window + self.__signal_window, len(super().get_data())), desc="Backtesting Progress"):
            close_price = close_prices.iloc[i]
            timestamp = timestamps.iloc[i]

            last_macd = super().get_data()['MACD'].iloc[i - 1]

            signal = "buy" if last_macd > 0 else "sell" if last_macd < 0 else 0

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

    def calculate_macd(self, close_prices):
        """
        Calculate MACD values and add them to the DataFrame.

        :param close_prices: Series containing closing prices.
        :return: MACD values.
        """
        short_ema = close_prices.ewm(span=self.__short_window, adjust=False).mean()
        long_ema = close_prices.ewm(span=self.__long_window, adjust=False).mean()
        macd = short_ema - long_ema
        signal_line = macd.ewm(span=self.__signal_window, adjust=False).mean()

        return macd - signal_line


class SMA_RSI_Strategy(SimpleSMALive, RSIStrategy):
    def __init__(self, pair, timeframe, sma=14, rsi_period=28):
        """
        Initialize Strategy3 object.

        :param pair: Trading pair (e.g., 'BTC/USD').
        :param timeframe: Timeframe for analysis (e.g., '1h').
        :param sma: Simple Moving Average parameter.
        :param rsi_period: RSI period for calculation.
        """
        # Initialize both parent classes
        self.__sma = sma
        self.__rsi_period = rsi_period
        self.__overbought_threshold = 70
        self.__oversold_threshold = 30

        SimpleSMALive.__init__(self, pair, timeframe, sma)
        RSIStrategy.__init__(self, pair, timeframe, rsi_period)

    def backtest(self, since):
        """
        Perform a backtest using a combination of Simple Moving Average (SMA) and Relative Strength Index (RSI) strategies.

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
        #print(close_prices)

        super().get_data()['RSI'] = self.calculate_rsi(close_prices)
        super().get_data()['SMA'] = close_prices.rolling(self.__sma).mean()

        for i in tqdm(range(self.__rsi_period, len(super().get_data())), desc="Backtesting Progress"):
            close_price = close_prices.iloc[i]
            timestamp = timestamps.iloc[i]

            last_sma = super().get_data()['SMA'].iloc[i - 1]
            #print(last_sma)
            signal1 = "buy" if close_price > last_sma else "sell" if close_price < last_sma else 0

            last_rsi = super().get_data()['RSI'].iloc[i - 1]
            #signal = self.generate_signal(last_rsi)
            signal2 = "buy" if last_rsi < self.__oversold_threshold else "sell" if last_rsi > self.__overbought_threshold else 0

            if signal1 == "buy" and signal2 == "buy" and not self.get_live_trade():
                self.set_live_trade(True)
                prix_achat = close_price
                print("buy")
                logging.info(f"Buy Signal: {timestamp}, Price: {prix_achat}")

            elif signal1 == "sell" and signal2 == "sell" and self.get_live_trade():
                self.set_live_trade(False)
                difference_de_prix = close_price - prix_achat
                frais_de_vente = 0.001  # Frais de vente de 0.1%
                difference_de_prix -= prix_achat * frais_de_vente  # Appliquer les frais
                print("sell")

                valeur_apres_vente = super().get_last_portfolio_value() + \
                                     super().get_last_portfolio_value() * difference_de_prix / prix_achat
                
                super().set_last_portfolio_value(valeur_apres_vente)
                self._portfolio_values.append(
                    (timestamp, round(prix_achat, 2), round(super().get_last_portfolio_value(), 2),
                    round(difference_de_prix, 2)))
                logging.info(
                    f"Sell Signal: {timestamp}, Price: {close_price}, Portfolio Value: {round(valeur_apres_vente, 2)}")

            else:
                print("0")

        logging.info("Backtest complete. Performance metrics:")
        logging.info(f"Initial Portfolio Value: {initial_portfolio_value}")
        logging.info(f"Final Portfolio Value: {round(super().get_last_portfolio_value(), 2)}")
        logging.info(f"Portfolio Return: {100 * (super().get_last_portfolio_value() / initial_portfolio_value - 1):.2f}")
        return

    def calculate_signal(self):
        """
        Calculate the combined signal based on both SMA and RSI.

        :return: Buy, sell, or hold signal.
        """
        # Calculate signals from both SMA and RSI
        sma_signal = super(SimpleSMALive, self).calculate_signal()
        #rsi_signal = RSIStrategy.calculate_signal(self)  # Use the class name directly instead of super()
        rsi_signal = super(RSIStrategy, self).generate_signal()

        # Combine signals (For simplicity, considering only buy and sell signals)
        if sma_signal == "buy" and rsi_signal == "buy":
            return "buy"
        elif sma_signal == "sell" and rsi_signal == "sell":
            return "sell"

        return 0

class MixStrategy(BaseStrategy):
    def __init__(self, pair, timeframe, sma, rsi_period=14, short_window=12, long_window=26, signal_window=9):
        """
        Initialize MixStrategy object.

        :param pair: Trading pair (e.g., 'BTC/USD').
        :param timeframe: Timeframe for analysis (e.g., '1h').
        :param sma: Simple Moving Average parameter.
        :param rsi_period: RSI period for calculation.
        :param short_window: Short window for MACD calculation.
        :param long_window: Long window for MACD calculation.
        :param signal_window: Signal window for MACD calculation.
        """
        super().__init__(pair, timeframe)
        self.sma_strategy = SimpleSMALive(pair, timeframe, sma)
        self.rsi_strategy = RSIStrategy(pair, timeframe, rsi_period)
        self.macd_strategy = MACDLive(pair, timeframe, short_window, long_window, signal_window)
        self._fees = 0.001  # 0.1% fees

    def backtest(self, since):
        """
        Perform a backtest using a combination of SMA, RSI, and MACD strategies.

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

        self.sma_strategy.set_data(super().get_data())
        self.rsi_strategy.set_data(super().get_data())
        self.macd_strategy.set_data(super().get_data())

        self.sma_strategy.backtest(since)
        self.rsi_strategy.backtest(since)
        self.macd_strategy.backtest(since)

        for i in tqdm(range(len(super().get_data())), desc="MixStrategy Backtesting Progress"):
            timestamp = timestamps.iloc[i]

            sma_signal = self.sma_strategy.calculate_signal()
            rsi_signal = self.rsi_strategy.calculate_signal()
            macd_signal = self.macd_strategy.calculate_signal()

            # Apply a combination strategy: buy if at least two strategies give a buy signal, sell if at least two give a sell signal
            signals = [sma_signal, rsi_signal, macd_signal]
            buy_signals = sum([1 for signal in signals if signal == "buy"])
            sell_signals = sum([1 for signal in signals if signal == "sell"])

            if buy_signals >= 2 and not self.get_live_trade():
                self.set_live_trade(True)
                prix_achat = close_prices.iloc[i]
                logging.info(f"Buy Signal: {timestamp}, Price: {prix_achat}")

            elif sell_signals >= 2 and self.get_live_trade():
                self.set_live_trade(False)
                difference_de_prix = close_prices.iloc[i] - prix_achat

                valeur_apres_vente = super().get_last_portfolio_value() + \
                                     super().get_last_portfolio_value() * difference_de_prix / prix_achat - self._fees

                super().set_last_portfolio_value(valeur_apres_vente)
                self._portfolio_values.append(
                    (timestamp, round(prix_achat, 2), round(super().get_last_portfolio_value(), 2),
                     round(difference_de_prix, 2)))
                logging.info(
                    f"Sell Signal: {timestamp}, Price: {close_prices.iloc[i]}, Portfolio Value: {round(valeur_apres_vente, 2)}")

        logging.info("MixStrategy Backtest complete. Performance metrics:")
        logging.info(f"Initial Portfolio Value: {initial_portfolio_value}")
        logging.info(f"Final Portfolio Value: {round(super().get_last_portfolio_value(), 2)}")
        logging.info(
            f"Portfolio Return: {100 * (super().get_last_portfolio_value() / initial_portfolio_value - 1):.2f}")
        return
