from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import pandas as pd
import api

class SimpleSMALive:
    def __init__(self, pair, timeframe, sma):
        self.__pair = pair
        self.__timeframe = timeframe
        self.__sma = sma
        self.__df = None
        self.__liveTrade = False
        self.__portfolio_values = []  # List to store portfolio values
        self.__last_portfolio_value = None  # To keep track of the last portfolio value
    def setLiveTrade(self, side):
        self.__liveTrade = side
    def getLiveTrade(self):
        return self.__liveTrade
    def backtest(self):
        print("backtest")
        # Reset portfolio values for a new backtest
        self.__portfolio_values = []

        # Load historical data for backtesting
        historical_data = api.getOHLCV(self.__pair, self.__timeframe, limit=500)#TODO creer une fonction qui récupere beaucoup de données sur la paire
        self.__df = historical_data.copy()

        for i in range(self.__sma, len(historical_data)):
            # Simulate receiving live data
            new_data = historical_data.iloc[i:i+1]
            self.__df = pd.concat([self.__df, new_data], ignore_index=True)

            # Calculate SMA signal
            signal = self.calculate_sma_signal()

            # Execute trades based on the signal (for simplicity, assuming constant position size)
            if signal == "buy" and not self.__liveTrade:
                self.setLiveTrade(True)
                self.__last_portfolio_value = new_data['Close'].values[0]
            elif signal == "sell" and self.__liveTrade:
                self.setLiveTrade(False)
                self.__portfolio_values.append(self.__last_portfolio_value / new_data['Close'].values[0])

        # Calculate final portfolio value
        final_portfolio_value = self.__last_portfolio_value if self.__liveTrade else historical_data['Close'].iloc[-1]
        self.__portfolio_values.append(final_portfolio_value / historical_data['Close'].iloc[-1])

        # Print or return performance metrics
        print("Backtest complete. Performance metrics:")
        print(f"Initial Portfolio Value: {historical_data['Close'].iloc[0]}")
        print(f"Final Portfolio Value: {final_portfolio_value}")
        print(f"Portfolio Return: {100 * (final_portfolio_value / historical_data['Close'].iloc[0] - 1):.2f}%")


    def calculate_sma_signal(self):
        if self.__df is None:
            self.__df = api.getOHLCV(self.__pair, self.__timeframe, limit=self.__sma + 1)
        # print(self.__df)
        new_data = api.getOHLCV(self.__pair, self.__timeframe,limit=1)
        self.__df = pd.concat([self.__df, new_data], ignore_index=True)
        self.__df = self.__df.drop_duplicates(subset=['Timestamp'], keep='last')

        self.__df['SMA'] = self.__df['Close'].rolling(self.__sma).mean()
        if self.__df is None or len(self.__df) == 0:
            print("DataFrame is empty or None.")
            return 0
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
    
