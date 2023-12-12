import pandas as pd
import api
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from tqdm import tqdm

class SimpleSMALive:
    def __init__(self, pair, timeframe, sma):
        """
        Initialize SimpleSMALive object.

        :param pair: Trading pair (e.g., 'BTC/USD').
        :param timeframe: Timeframe for analysis (e.g., '1h').
        :param sma: Simple Moving Average parameter.
        """
        self.__pair = pair
        self.__timeframe = timeframe
        self.__sma = sma
        self.__df = None
        self.__liveTrade = False
        self.__portfolio_values = []  # List to store portfolio values
        self.__last_portfolio_value = 1000  # To keep track of the last portfolio value

    def set_live_trade(self, side):
        """
        Set the live trade status.

        :param side: Boolean indicating the live trade status.
        """
        self.__liveTrade = side

    def get_live_trade(self):
        """
        Get the live trade status.

        :return: Boolean indicating the live trade status.
        """
        return self.__liveTrade

    def backtest(self):
        """
        Perform backtesting and update portfolio values.
        """
        print("Calculating backtest ...")
        since = '2022-07-21 00:00:00'
        self.__portfolio_values = []

        # Generate output directory based on pair and timeframe
        pair_dir = self.__pair.replace('/', '_')
        output_dir = f"{pair_dir}_data"

        # Generate output filename based on pair, timeframe, and start date
        filename = f"{pair_dir}_{self.__timeframe}_{since.replace(':', '-').replace(' ', '_')}.csv"

        # Use os.path.join to create the full path
        path = os.path.join(output_dir, filename)
        print(path)

        # Load historical data for backtesting
        if not os.path.exists(path):
            print("Need to download data...")
            historical_data = api.get_historical_data(self.__pair, self.__timeframe, since)
        else:
            print("Using existing data...")
            historical_data = pd.read_csv(path)

        self.__df = historical_data.copy()

        initial_portfolio_value = 1000
        self.__last_portfolio_value = initial_portfolio_value
        print(f"Initial Portfolio Value: {initial_portfolio_value}")

        close_prices = historical_data['Close']
        timestamps = historical_data['Timestamp']

        self.__df['SMA'] = close_prices.rolling(self.__sma).mean()

        for i in tqdm(range(self.__sma, len(historical_data)), desc="Backtesting Progress"):
            close_price = close_prices.iloc[i]
            timestamp = timestamps.iloc[i]

            last_sma = self.__df['SMA'].iloc[i-1]
            signal = "buy" if close_price > last_sma else "sell" if close_price < last_sma else 0

            if signal == "buy" and not self.__liveTrade:
                self.set_live_trade(True)
                prix_achat = close_price

            elif signal == "sell" and self.__liveTrade:
                self.set_live_trade(False)
                difference_de_prix = close_price - prix_achat
                valeur_apres_vente = self.__last_portfolio_value + self.__last_portfolio_value * difference_de_prix / prix_achat
                self.__last_portfolio_value = valeur_apres_vente
                self.__portfolio_values.append((timestamp, round(prix_achat, 2), round(self.__last_portfolio_value, 2), round(difference_de_prix, 2)))

        print("Backtest complete. Performance metrics:")
        print(f"Initial Portfolio Value: {initial_portfolio_value}")
        print(f"Final Portfolio Value: {round(self.__last_portfolio_value, 2)}")
        print(f"Portfolio Return: {100 * (self.__last_portfolio_value / initial_portfolio_value - 1):.2f}%")
        return

    def plot_figure(self):
        """
        Plot a figure showing candlestick chart, portfolio values, and portfolio changes.
        """
        sell, prix, portfolio_values, changes = zip(*self.__portfolio_values)
        dates = self.__df.index

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
        # fig.add_trace(go.Candlestick(x=dates,
                    #                  open=self.__df['Open'],
                    #                  high=self.__df['High'],
                    #                  low=self.__df['Low'],
                    #                  close=self.__df['Close'],
                    #                  name=f'{self.__pair} Candlestick'),
                    #   row=1, col=1)
        fig.add_trace(go.Scatter(x=dates, y = self.__df['Close'], mode='lines', name=f"Values of {self.__pair}"), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell, y=portfolio_values, mode='lines', name='Portfolio Values'), row=2, col=1)
        fig.add_trace(go.Bar(x=sell, y=changes, name='Portfolio Changes'), row=3, col=1)
        title = 'Backtest ' + self.__pair
        fig.update_layout(title_text=title, showlegend=True)
        fig.update_layout(xaxis_rangeslider_visible=False)
        # print("out")
        return fig

    def calculate_signal(self):
        """
        Calculate SMA signal based on the current data.

        :return: Buy, sell, or hold signal.
        """
        self.update_data()
        if self.is_data_empty():
            return 0

        self.calculate_sma()
        signal = self.generate_signal()
        return signal

    def update_data(self):
        """
        Update historical data for SMA calculation.
        """
        if self.__df is None:
            self.__df = api.get_ohlcv(self.__pair, self.__timeframe, limit=self.__sma + 1)
        new_data = api.get_ohlcv(self.__pair, self.__timeframe, limit=1)
        self.__df = pd.concat([self.__df, new_data], ignore_index=True)
        self.__df = self.__df.drop_duplicates(subset=['Timestamp'], keep='last')

    def is_data_empty(self):
        """
        Check if historical data is empty.

        :return: True if data is empty, False otherwise.
        """
        if self.__df is None or len(self.__df) == 0:
            print("DataFrame is empty or None.")
            return True
        return False

    def calculate_sma(self):
        """
        Calculate SMA values and add them to the DataFrame.
        """
        self.__df['SMA'] = self.__df['Close'].rolling(self.__sma).mean()

    def generate_signal(self):
        """
        Generate buy, sell, or hold signal based on SMA values.

        :return: Buy, sell, or hold signal.
        """
        last_value = self.__df['Close'].iloc[-1]
        last_sma = self.__df['SMA'].iloc[-2]

        if pd.isnull(last_sma):
            return 0

        if last_value > last_sma:
            return "buy"
        elif last_value < last_sma:
            return "sell"

        return 0

    def __del__(self):
        """
        Destructor method.
        """
        return
