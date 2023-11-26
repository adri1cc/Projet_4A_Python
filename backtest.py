from __future__ import print_function
from pyalgotrade.stratanalyzer import returns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategies import *
import api
from pandas import  read_csv
from  bar_feed import *
import datetime
from matplotlib import dates as mPlotDATEs


#TODO create function that download pair and return a feed sur une plage de temps donnée
#TODO gerer si les fichiers de donnée existe deja ou pas

def getFeed(instrument, timeframe):
    df = api.getOHLCV(instrument, timeframe)
    csv_filename = instrument.replace('/', '-') + '.csv'
    df.to_csv(csv_filename, index=False)
    df = read_csv(csv_filename, parse_dates=[0], index_col=0)
    df["Index"] = df.index
    feed = DataFrameBarFeed(df, instrument, barfeed.Frequency.DAY) 
    return feed

def timestamp_converter(aString):
    if isinstance(aString, bytes):
        aString = aString.decode('utf-8')  # Adjust the encoding if necessary
    return mPlotDATEs.date2num(datetime.datetime.strptime(aString, "%Y-%m-%d %H:%M:%S"))

def run_strategy(smaPeriod, instrument):
 

    feed = getFeed(instrument,"5m")
    # Evaluate the strategy with the feed.
    portfolio = 100000
    myStrategy = MyStrategy(feed, instrument, smaPeriod, portfolio)
    
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