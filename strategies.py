import pandas as pd
import api
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

class SimpleSMALive:
    def __init__(self, pair, timeframe, sma):
        self.__pair = pair
        self.__timeframe = timeframe
        self.__sma = sma
        self.__df = None
        self.__liveTrade = False
        self.__portfolio_values = []  # List to store portfolio values
        self.__last_portfolio_value = 1000  # To keep track of the last portfolio value
    def setLiveTrade(self, side):
        self.__liveTrade = side
    def getLiveTrade(self):
        return self.__liveTrade
    def backtest(self):
        print("Calcul backtest ...")
        # Reset portfolio values for a new backtest
        self.__portfolio_values = []
        csv_file_path = r'BTC_USDT_data\BTC_USDT_5m_2022-07-21 00-00-00.csv'
        # Load historical data for backtesting
        # historical_data = backtest.getData(self.__pair, self.__timeframe)
        if not os.path.exists(csv_file_path):
            print("Need to download data...")
            historical_data = api.getHistoricalData(self.__pair,self.__timeframe,'2022-07-21 00:00:00')
        historical_data =pd.read_csv(csv_file_path)            

        new_data = pd.DataFrame(columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'SMA'])

        self.__df = historical_data.copy()
        
        initial_portfolio_value = 1000
        self.__last_portfolio_value = initial_portfolio_value
        print(f"Initial Portfolio Value: {initial_portfolio_value}")
        # print("le gggggg")
        # print(self.__df)
        for i in range(self.__sma, len(historical_data)):
            # Simulate receiving live data
            new_data = historical_data.iloc[i:i+1].copy()

            self.__df = pd.concat([self.__df, new_data])

            # Calculate SMA signal
            self.calculate_sma()
            signal = self.generate_signal()

            # Execute trades based on the signal (for simplicity, assuming constant position size)
            if signal == "buy" and not self.__liveTrade:
                self.setLiveTrade(True)
                # Enregistrer le prix d'achat
                prix_achat = new_data['Close'].values[0]

            elif signal == "sell" and self.__liveTrade:
                self.setLiveTrade(False)

                # Calculer la différence de prix entre l'achat et la vente
                difference_de_prix = new_data['Close'].values[0] - prix_achat
                time = new_data.index[-1]

                # Enregistrer la valeur actuelle du portefeuille après la vente
                valeur_apres_vente = self.__last_portfolio_value + self.__last_portfolio_value*difference_de_prix/prix_achat
                self.__last_portfolio_value=valeur_apres_vente
                self.__portfolio_values.append((time,
                    round(prix_achat, 2),
                    round(self.__last_portfolio_value, 2),
                    round(difference_de_prix, 2)
                ))
        
        # Print or return performance metrics
        print("Backtest complete. Performance metrics:")
        print(f"Initial Portfolio Value: {initial_portfolio_value}")
        print(f"Final Portfolio Value: {round(self.__last_portfolio_value,2)}")
        print(f"Portfolio Return: {100 * (self.__last_portfolio_value / initial_portfolio_value - 1):.2f}%")
        print("Cumulative Portfolio Values Over Time:", self.__portfolio_values)
        return 
    
    def plot_figure(self):
                # Divisez les données en trois listes distinctes pour les dates, les valeurs du portefeuille et les variations
        sell, prix, portfolio_values, changes = zip(*self.__portfolio_values)
        dates = self.__df.index

        # Créez une figure avec deux sous-graphiques (un pour les valeurs du portefeuille, un pour les variations)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
        fig.add_trace(go.Candlestick(x=dates,
                    open=self.__df['Open'],
                    high=self.__df['High'],
                    low=self.__df['Low'],
                    close=self.__df['Close'],
                    name=f'{self.__pair} Candlestick'),
                    row=1, col=1)
        fig.add_trace(go.Scatter(x=sell, y=portfolio_values, mode='lines', name='Portfolio Values'), row=2, col=1)
        fig.add_trace(go.Bar(x=sell, y=changes, name='Portfolio Changes'), row=3, col=1)
        title = 'Backtest '+ self.__pair
        fig.update_layout(title_text=title, showlegend=True)
        fig.update_layout(xaxis_rangeslider_visible=False)
        print("out")
        return fig

    def calculate_sma_signal(self):
        self.update_data()
        if self.is_data_empty():
            return 0

        self.calculate_sma()
        signal = self.generate_signal()
        return signal

    def update_data(self):
        if self.__df is None:
            self.__df = api.getOHLCV(self.__pair, self.__timeframe, limit=self.__sma + 1)
        new_data = api.getOHLCV(self.__pair, self.__timeframe, limit=1)
        self.__df = pd.concat([self.__df, new_data], ignore_index=True)
        self.__df = self.__df.drop_duplicates(subset=['Timestamp'], keep='last')

    def is_data_empty(self):
        if self.__df is None or len(self.__df) == 0:
            print("DataFrame is empty or None.")
            return True
        return False

    def calculate_sma(self):
        self.__df['SMA'] = self.__df['Close'].rolling(self.__sma).mean()

    def generate_signal(self):
        last_value = self.__df['Close'].iloc[-1]
        last_sma = self.__df['SMA'].iloc[-2]

        if pd.isnull(last_sma):
            # print("last sma null")
            return 0

        if last_value > last_sma:
            return "buy"
        elif last_value < last_sma:
            return "sell"

        return 0
    
    def __del__(self):
        return