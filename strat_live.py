from pickletools import long1
import time
from api import *
import pandas as pd


df = None
live_trade = False

def create_trading_logic():
    return {'stop_flag': False}

def start_trade(trading_logic):
    while not trading_logic['stop_flag']:
        print("Live trading is running")
        SimpleSMALive("BTC/USDT","5m",5)
        #time.sleep(2)
    print("Live trading is stopped")

def stop_trade(trading_logic):
    trading_logic['stop_flag'] = True

def SimpleSMALive(pair, timeframe, sma):
    global df
    global live_trade
    if df is None:
        df = getOHLCV(pair, timeframe, limit=sma+1)

    df = pd.concat([df, getOHLCV(pair, timeframe, limit=1)], ignore_index=True)
    print(df["Close"])

    df['SMA'] = df['Close'].rolling(sma).mean()
    
    last_value = df['Close'].iloc[-1]
    last_sma = df['SMA'].iloc[-1]
    print(f"SMA {last_sma} CLose {last_value}")
    # print(df)
    if last_sma is None:
        print("last sma null")
        return
    
    if live_trade is False:
        print("live_trade false")

        if  last_value > last_sma:

            if getQuantity(pair,"buy")>0:
                print("lunch buy order")
                #place_order(pair, "buy", 6, "market")
                live_trade = True

            else:
                print("Not enought founds") 

    elif last_value < last_sma:
        if getQuantity(pair,"sell")>0:
                print("lunch sell order")
                #place_order(pair, "sell", 6, "market")
                live_trade = False

    return 

last_value = 0
last_sma =0

# SimpleSMALive("BTC/USDT", "5m", 10)