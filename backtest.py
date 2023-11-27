from __future__ import print_function
from pyalgotrade.stratanalyzer import returns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategies import *
import api
from pandas import  Timestamp, read_csv
from  bar_feed import *
import datetime
from matplotlib import dates as mPlotDATEs
import os
import pandas as pd


def getFeed(instrument, timeframe,since: int | None = None, limit: int | None = None):
    csv_filename = instrument.replace('/', '-') + str(since) + str(limit) + '.csv'
    if not os.path.exists(csv_filename):
        df = api.getOHLCV(instrument, timeframe, since, limit)
        df.to_csv(csv_filename, index=False)
    df = read_csv(csv_filename, parse_dates=[0], index_col=0)
    df["Index"] = df.index
    feed = DataFrameBarFeed(df, instrument, barfeed.Frequency.DAY) 
    return feed,df

def convert_date_string_to_timestamp(date_string):
    # Convert the date string to a datetime object
    dt_object = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    # Convert the datetime object to a timestamp in milliseconds
    timestamp_milliseconds = int(dt_object.timestamp() * 1000)

    return timestamp_milliseconds

def timestamp_converter(aString):
    if isinstance(aString, bytes):
        aString = aString.decode('utf-8')  # Adjust the encoding if necessary
    return mPlotDATEs.date2num(datetime.datetime.strptime(aString, "%Y-%m-%d %H:%M:%S"))

def run_strategy(smaPeriod, instrument):
 
    date_string = "2023-05-01 00:00:00"
    timestamp = convert_date_string_to_timestamp(date_string)
    feed,df = getFeed(instrument,"5m",timestamp,5000)
    print(df['Close'])
    # Evaluate the strategy with the feed.
    portfolio = 100000
    myStrategy = MyStrategy(feed, instrument, smaPeriod, portfolio)
    
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    myStrategy.run()
    portfolio_values = myStrategy.getPortfolioValues()
    final = (myStrategy.getBroker().getEquity()-100000)/1000

    print("Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity())
    print(f"PnL: {final:.2f} %")
    # Divisez les données en trois listes distinctes pour les dates, les valeurs du portefeuille et les variations
    dates, portfolio_values, changes = zip(*portfolio_values)
    # print(dates)

    # Créez une figure avec deux sous-graphiques (un pour les valeurs du portefeuille, un pour les variations)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
    fig.add_trace(go.Candlestick(x=df['Index'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=f'{instrument} Candlestick'),
                row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=portfolio_values, mode='lines', name='Portfolio Values'), row=2, col=1)
    fig.add_trace(go.Bar(x=dates, y=changes, name='Portfolio Changes'), row=3, col=1)
    title = 'Backtest '+ myStrategy.getName()
    fig.update_layout(title_text=title, showlegend=True)
    fig.update_layout(xaxis_rangeslider_visible=False)

    return fig