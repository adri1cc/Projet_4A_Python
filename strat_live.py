from pickletools import long1
import time
from api import *
import pandas as pd
from strategies import SimpleSMALive

df = None
live_trade = False
result = None

def create_trading_logic():
    return {'stop_flag': False}

def start_trade(trading_logic, pair, strategy):
    global live_trade
    global result
    sma = SimpleSMALive(pair, "5m", 10) 
    print("Live trading is running")
    while not trading_logic['stop_flag']:
        # print("Live trading is running")
        if strategy == 'SimpleSMA': #Probablement une zone a améliorer elle est check a chques fois
            # print("SimpleSMA")
            result = sma.calculate_sma_signal()
        elif strategy == 'Stratégie 2':
            print("Startégie 2 is not implemented")
        elif strategy == 'Stratégie 3':
            print("Startégie 3 is not implemented")
        
        if sma.getLiveTrade() is False:
            # print("live_trade false")

            if  result=="buy":
                quantity_buy = getQuantity(pair,"buy")
                investment=getInvestment(quantity_buy,100)
                if investment>6:
                    print("lunch buy order")
                    
                    #place_order(pair, "buy", 6, "market")
                    sma.setLiveTrade(True)

                else:
                    print("Not enought founds") 

        elif result=="sell":
            quantity_sell = getQuantity(pair,"sell")

            if quantity_sell>0:
                print("lunch sell order")
                #place_order(pair, "sell", 6, "market")
                sma.setLiveTrade(False)
            else:
                print("Not enought founds")
    print("Live trading is stopped")
    del sma
    return

def stop_trade(trading_logic):
    global df
    trading_logic['stop_flag'] = True
    df = None

def getInvestment(quantity, percent):
    investment = quantity*percent/100
    # print(investment)
    if investment<6:
        investment=6
    # print(investment)
    return investment

# def SimpleSMALive(pair, timeframe, sma):
#     global df
#     if df is None:
#         df = getOHLCV(pair, timeframe, limit=sma+1)

#     df = pd.concat([df, getOHLCV(pair, timeframe, limit=1)], ignore_index=True)
#     # print(df)
#     df = df.drop_duplicates(subset=['Timestamp'], keep='last')

#     # print(df)
#     df['SMA'] = df['Close'].rolling(sma).mean()
    
#     last_value = df['Close'].iloc[-1]
#     last_sma = df['SMA'].iloc[-2]
#     # print(f"SMA {last_sma} CLose {last_value}")
#     # print(df)
#     if last_sma is None:
#         print("last sma null")
#         return 0

#     if  last_value > last_sma:
#         return "buy"

#     elif last_value < last_sma:
#         return "sell"

#     return 0

last_value = 0
last_sma =0