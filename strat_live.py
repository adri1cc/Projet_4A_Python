import time
from api import *
df = None

def create_trading_logic():
    return {'stop_flag': False}

def start_trade(trading_logic):
    while not trading_logic['stop_flag']:
        print("Live trading is running")
        SimpleSMALive()
        time.sleep(2)
    print("Live trading is stopped")

def stop_trade(trading_logic):
    trading_logic['stop_flag'] = True

def SimpleSMALive(pair, timeframe, sma):
    if df is None:
        df = getOHLCV(pair, timeframe, limit=sma+1)
    df = df + getOHLCV(pair, timeframe, limit=1)
    df['SMA'].df['Close'].rolling(sma).mean() #A test avec open high et low
    last_value = df['close'].iloc[-1]
    if  last_value > 
    return 