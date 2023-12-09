from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import pandas as pd
import api
import backtest
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

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

        # Load historical data for backtesting
        historical_data = backtest.getData(self.__pair, self.__timeframe)
        # print("histo")
        # print(historical_data)
        new_data = pd.DataFrame(columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'SMA'])

        self.__df = historical_data.copy()
        
        # print("le fff")
        # print(len(historical_data))
            # Print initial portfolio value
        initial_portfolio_value = 1000
        self.__last_portfolio_value = initial_portfolio_value
        print(f"Initial Portfolio Value: {initial_portfolio_value}")
        print("le gggggg")
        print(self.__df)
        for i in range(self.__sma, len(historical_data)):
            # Simulate receiving live data
            new_data = historical_data.iloc[i:i+1].copy()

            # print("before")
            #  print(self.__df)
            # Assuming 'Timestamp' is already part of self.__df due to the previous addition
            self.__df = pd.concat([self.__df, new_data])

            # print("after") 
            # print(self.__df)
            # Calculate SMA signal
            self.calculate_sma()
            signal = self.generate_signal()

            # Execute trades based on the signal (for simplicity, assuming constant position size)
            if signal == "buy" and not self.__liveTrade:
                self.setLiveTrade(True)
                # Enregistrer le prix d'achat
                prix_achat = new_data['Close'].values[0]
                # ... votre logique d'achat ici ...

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

                # Mettre à jour la valeur initiale du portefeuille
                # initial_portfolio_value = valeur_apres_vente
            # Print portfolio value after each iteration
            # print(f"Portfolio Value after iteration {i}: {self.__last_portfolio_value}")


        # Calculate cumulative portfolio values
        # cumulative_portfolio_values_over_time = self.calculate_portfolio_value(initial_portfolio_value)
        
        # Print or return performance metrics
        print("Backtest complete. Performance metrics:")
        print(f"Initial Portfolio Value: {initial_portfolio_value}")
        print(f"Final Portfolio Value: {round(self.__last_portfolio_value,2)}")
        print(f"Portfolio Return: {100 * (self.__last_portfolio_value / initial_portfolio_value - 1):.2f}%")
        print("Cumulative Portfolio Values Over Time:", self.__portfolio_values)
        print(len(self.__portfolio_values))
        return 
    
    def plot_figure(self):
        # print("inside")
                # Divisez les données en trois listes distinctes pour les dates, les valeurs du portefeuille et les variations
        sell, prix, portfolio_values, changes = zip(*self.__portfolio_values)
        # print("inbetween")
        # print(self.__df)
        # print("daet")
        dates = self.__df.index
        # print("dates :")
        # print(dates)

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

    def calculate_portfolio_value(self, initial_portfolio_value):
        # Calculate cumulative portfolio value based on the performance values recorded during backtest
        relative_performance = np.array(self.__portfolio_values)
        cumulative_portfolio_values = np.cumprod(relative_performance) * initial_portfolio_value

        return cumulative_portfolio_values.tolist()
    
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

class SimpleSMA(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod, portfolio):
        super(SimpleSMA, self).__init__(feed, portfolio)
        self.__position = None
        self.__instrument = instrument
        self.__smaPeriod = smaPeriod
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)
        self.__portfolio_values = []  # List to store portfolio values
        self.__last_portfolio_value = None  # To keep track of the last portfolio value

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        # self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        # self.info("SELL at $%.2f" % (execInfo.getPrice()))

        # Calculate the new portfolio value and store it
        new_portfolio_value = self.getBroker().getEquity()
        if self.__last_portfolio_value is not None:
            portfolio_change = new_portfolio_value - self.__last_portfolio_value
            self.__portfolio_values.append((execInfo.getDateTime(), new_portfolio_value, portfolio_change))

        self.__last_portfolio_value = new_portfolio_value
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        #print("Received bars:", bars)
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for 1 share. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 1, True)
        # Check if we have to exit the position.
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            self.__position.exitMarket()

    def getPortfolioValues(self):
        return self.__portfolio_values

    def getSMA(self):
        return self.__sma
    def getName(self):
        return self.__instrument + " " + "SimpleSMA" + " " + str(self.__smaPeriod)
    
