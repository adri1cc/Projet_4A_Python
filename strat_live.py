import api
import strategies

result = None

def create_trading_logic():
    """
    Create a dictionary to hold trading logic parameters.
    """
    return {'stop_flag': False}

def backtest(value, timeframe, pair):
    """
    Perform backtesting using SimpleSMALive strategy.
    
    :param value: Some value.
    :param timeframe: Timeframe for backtesting.
    :param pair: Trading pair for backtesting.
    :return: Figure object for plotting.
    """
    sma = strategies.SimpleSMALive(pair, timeframe, value)
    sma.backtest()
    fig = sma.plot_figure()
    return fig

def start_trade(trading_logic, timeframe, pair, strategy):
    """
    Start live trading based on the specified strategy.
    
    :param trading_logic: Dictionary holding trading logic parameters.
    :param timeframe: Timeframe for live trading.
    :param pair: Trading pair for live trading.
    :param strategy: Trading strategy to use (e.g., 'SimpleSMA').
    """
    global result
    sma = strategies.SimpleSMALive(pair, timeframe, 10)
    print("Live trading is running")
    
    while not trading_logic['stop_flag']:
        print("Live trading is running")
        
        if strategy == 'SimpleSMA':  # Probably a zone to improve, as it is checked every time
            result = sma.calculate_sma_signal()
        elif strategy == 'Strategy 2':
            print("Strategy 2 is not implemented")
        elif strategy == 'Strategy 3':
            print("Strategy 3 is not implemented")
        
        if sma.getLiveTrade() is False:
            if result == "buy":
                quantity_buy = api.get_quantity(pair, "buy")
                investment = get_investment(quantity_buy, 100)  # TODO: Set the risk percentage as a parameter
                
                if investment > 6:
                    print("Launch buy order")
                    # place_order(pair, "buy", 6, "market")
                    sma.setLiveTrade(True)
                else:
                    print("Not enough funds")
        elif result == "sell":
            quantity_sell = api.get_quantity(pair, "sell")
            
            if quantity_sell > 0:
                print("Launch sell order")
                # place_order(pair, "sell", 6, "market")
                sma.setLiveTrade(False)
            else:
                print("Not enough funds")
                
    print("Live trading is stopped")
    del sma

def stop_trade(trading_logic):
    """
    Stop live trading by setting the stop flag.
    
    :param trading_logic: Dictionary holding trading logic parameters.
    """
    trading_logic['stop_flag'] = True

def get_investment(quantity, percent):
    """
    Calculate the investment based on quantity and percentage.
    
    :param quantity: Quantity of the asset.
    :param percent: Percentage of the investment.
    :return: Calculated investment amount.
    """
    investment = quantity * percent / 100
    if investment < 6:
        investment = 6
    return investment
