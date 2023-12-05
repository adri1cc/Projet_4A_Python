from pickletools import long1
import time
from api import *
import pandas as pd


df = None
live_trade = False

def create_trading_logic():
    return {'stop_flag': False}

# TODO add pair and strategy
def start_trade(trading_logic, pair):
    global live_trade
    while not trading_logic['stop_flag']:
        print("Live trading is running")
           
        result = SimpleSMALive(pair, "5m", 10) 
        #TODO a ajouter les possibilités de plusieurs stratégies (switch case)
        
        if live_trade is False:
            # print("live_trade false")

            if  result=="buy":

                if getQuantity(pair,"buy")>0:
                    print("lunch buy order")
                    #place_order(pair, "buy", 6, "market")
                    live_trade = True

                else:
                    print("Not enought founds") 

        elif result=="sell":
            if getQuantity(pair,"sell")>0:
                print("lunch sell order")
                #place_order(pair, "sell", 6, "market")
                live_trade = False
            else:
                print("Not enought founds")
    print("Live trading is stopped")
    return

def stop_trade(trading_logic):
    global df
    trading_logic['stop_flag'] = True
    df = None

def SimpleSMALive(pair, timeframe, sma):
    global df
    if df is None:
        df = getOHLCV(pair, timeframe, limit=sma+1)

    df = pd.concat([df, getOHLCV(pair, timeframe, limit=1)], ignore_index=True)
    # print(df)
    df = df.drop_duplicates(subset=['Timestamp'], keep='last')

    # print(df)
    df['SMA'] = df['Close'].rolling(sma).mean()
    
    last_value = df['Close'].iloc[-1]
    last_sma = df['SMA'].iloc[-2]
    # print(f"SMA {last_sma} CLose {last_value}")
    # print(df)
    if last_sma is None:
        print("last sma null")
        return 0

    if  last_value > last_sma:
        return "buy"

    elif last_value < last_sma:
        return "sell"

    return 0

last_value = 0
last_sma =0