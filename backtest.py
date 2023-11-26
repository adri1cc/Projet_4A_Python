from __future__ import print_function
from pyalgotrade import strategy
from pyalgotrade.barfeed import quandlfeed
from pyalgotrade.technical import ma
from pyalgotrade import plotter
from pyalgotrade.barfeed import quandlfeed
from pyalgotrade.stratanalyzer import returns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategies import *

#TODO create function that download pair and return a feed sur une plage de temps donnée




def run_strategy(smaPeriod):
    # Load the bar feed from the CSV file
    feed = quandlfeed.Feed()
    feed.addBarsFromCSV("BTC/USD", "BTC-USD.csv")
    # Evaluate the strategy with the feed.
    portfolio = 100000
    myStrategy = MyStrategy(feed, "BTC/USD", smaPeriod, portfolio)
    
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    myStrategy.run()
    portfolio_values = myStrategy.getPortfolioValues()
    final = (myStrategy.getBroker().getEquity()-100000)/1000

    print("Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity())
    print(f"PnL(en %): {final:.2f}")
    # Divisez les données en trois listes distinctes pour les dates, les valeurs du portefeuille et les variations
    dates, portfolio_values, changes = zip(*portfolio_values)

    # Créez une figure avec deux sous-graphiques (un pour les valeurs du portefeuille, un pour les variations)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=['Portfolio Values', 'Portfolio Changes'])
    fig.add_trace(go.Scatter(x=dates, y=portfolio_values, mode='lines', name='Portfolio Values'), row=1, col=1)
    fig.add_trace(go.Bar(x=dates, y=changes, name='Portfolio Changes'), row=2, col=1)
    title = 'Backtest '+ myStrategy.getName()
    fig.update_layout(title_text=title, showlegend=True)

    return fig