from __future__ import print_function

from pyalgotrade import strategy
from pyalgotrade.barfeed import quandlfeed
from pyalgotrade.technical import ma
from pyalgotrade import plotter
from pyalgotrade.barfeed import quandlfeed
from pyalgotrade.stratanalyzer import returns
from strategies import *



def run_strategy(smaPeriod):
    # Load the bar feed from the CSV file
    feed = quandlfeed.Feed()
    feed.addBarsFromCSV("BTC/USD", "BTC-USD.csv")
    portfolio = 100000
    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, "BTC/USD", smaPeriod, portfolio)
    
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(myStrategy)
    # Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
    plt.getInstrumentSubplot("BTC/USD").addDataSeries("SMA", myStrategy.getSMA())
    # Plot the simple returns on each bar.
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

    myStrategy.run()
    print("Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity())
    final = (myStrategy.getBroker().getEquity()-100000)/1000
    print(f"PnL(en %): {final:.2f}")
    plt.plot()

run_strategy(2)

# feed = quandlfeed.Feed()
# feed.addBarsFromCSV("BTC/USD", "BTC-USD.csv")
# # Evaluate the strategy with the feed's bars.
# myStrategy = sma_crossover.SMACrossOver(feed, "BTC/USD", 20)

# # Attach a returns analyzers to the strategy.
# returnsAnalyzer = returns.Returns()
# myStrategy.attachAnalyzer(returnsAnalyzer)

# # Attach the plotter to the strategy.
# plt = plotter.StrategyPlotter(myStrategy)
# # Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
# plt.getInstrumentSubplot("BTC/USD").addDataSeries("SMA", myStrategy.getSMA())
# # Plot the simple returns on each bar.
# plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

# # Run the strategy.
# myStrategy.run()
# myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

# # Plot the strategy.
# plt.plot()