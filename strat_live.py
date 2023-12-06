from pickletools import long1
import time
from api import *
import pandas as pd
from strategies import SimpleSMALive

result = None

def create_trading_logic():
    return {'stop_flag': False}

def start_trade(trading_logic, pair, strategy):
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
            sma.backtest()

            if  result=="buy":
                quantity_buy = getQuantity(pair,"buy")
                investment=getInvestment(quantity_buy,100)#TODO mettre le pourcentage de risque en parametre
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
    trading_logic['stop_flag'] = True

def getInvestment(quantity, percent):
    investment = quantity*percent/100
    # print(investment)
    if investment<6:
        investment=6
    # print(investment)
    return investment
