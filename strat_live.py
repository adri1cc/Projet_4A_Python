import api 
import strategies

result = None

def create_trading_logic():
    return {'stop_flag': False}

def backtest(value, timeframe, pair):
    sma = strategies.SimpleSMALive(pair, timeframe, value)
    sma.backtest()
    fig = sma.plot_figure()
    return fig

def start_trade(trading_logic, timeframe, pair, strategy):
    global result
    sma = strategies.SimpleSMALive(pair, timeframe, 10) 
    print("Live trading is running")
    while not trading_logic['stop_flag']:
        print("Live trading is running")
        if strategy == 'SimpleSMA': #Probablement une zone a améliorer elle est check a chques fois
            result = sma.calculate_sma_signal()
        elif strategy == 'Stratégie 2':
            print("Startégie 2 is not implemented")
        elif strategy == 'Stratégie 3':
            print("Startégie 3 is not implemented")
        
        if sma.getLiveTrade() is False:

            if  result=="buy":
                quantity_buy = api.getQuantity(pair,"buy")
                investment=getInvestment(quantity_buy,100)#TODO mettre le pourcentage de risque en parametre

                if investment>6:
                    print("lunch buy order")
                    #place_order(pair, "buy", 6, "market")
                    sma.setLiveTrade(True)
                else:
                    print("Not enought founds") 

        elif result=="sell":
            quantity_sell = api.getQuantity(pair,"sell")

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
    if investment<6:
        investment=6
    return investment
