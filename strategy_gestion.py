"""
This script contains the code for the strategy gestion.
"""
import logging
import api
import strategies

result = None

def create_trading_logic():
    """
    Create a dictionary to hold trading logic parameters.
    
    Example:
    >>> trading_logic = create_trading_logic()
    >>> isinstance(trading_logic, dict)
    True
    >>> trading_logic['stop_flag']
    False
    """
    return {'stop_flag': False}

def backtest(value, timeframe, pair, strategy, date):
    """
    Perform backtesting using SimpleSMALive strategy.
    
    :param value: Some value.
    :param timeframe: Timeframe for backtesting.
    :param pair: Trading pair for backtesting.
    :return: Figure object for plotting.

    Example:
    >>> fig = backtest(10, '1h', 'BTC/USDT', 'SimpleSMA', '2022-01-01')
    >>> isinstance(fig, strategies.SimpleSMALive)
    True
    """
    strategies_dict = {
        'SimpleSMA': strategies.SimpleSMALive,
    }

    if strategy not in strategies_dict:
        raise NotImplementedError(f"{strategy} is not implemented")

    strategy_instance = strategies_dict[strategy](pair, timeframe, value)
    strategy_instance.backtest(date)
    fig = strategy_instance.plot_figure()
    return fig

def start_trade(trading_logic, timeframe, pair, strategy, percentage):
    """
    Start live trading based on the specified strategy.

    :param trading_logic: Dictionary holding trading logic parameters.
    :param timeframe: Timeframe for live trading.
    :param pair: Trading pair for live trading.
    :param strategy: Trading strategy to use (e.g., 'SimpleSMA').
    
    Example:
    >>> trading_logic = create_trading_logic()
    >>> start_trade(trading_logic, '1h', 'BTC/USDT', 'SimpleSMA', 5)
    """
    investment_threshold = 6
    
    strategies_dict = {
        'SimpleSMA': strategies.SimpleSMALive,
    }

    if strategy not in strategies_dict:
        raise NotImplementedError(f"{strategy} is not implemented")

    strategy_instance = strategies_dict[strategy](pair, timeframe, 10)

    while not trading_logic['stop_flag']:
        logging.info("Live trading is running")

        result = strategy_instance.calculate_signal()

        if not strategy_instance.get_live_trade():

            if result == "buy":
                quantity_buy = api.get_quantity(pair, "buy")
                investment = get_investment(quantity_buy, percentage) 
                logging.info("Launch buy order")
                # place_order(pair, "buy", investment, "market")
                strategy_instance.set_live_trade(True)

        elif result == "sell":
            quantity_sell = api.get_quantity(pair, "sell")

            if quantity_sell > 0:
                logging.info("Launch sell order")
                # place_order(pair, "sell", investment, "market")
                strategy_instance.set_live_trade(False)
                
            else:
                logging.info("Not enough funds")

    logging.info("Live trading is stopped")
    del strategy_instance
    
def stop_trade(trading_logic):
    """
    Stop live trading by setting the stop flag.
    
    :param trading_logic: Dictionary holding trading logic parameters.
    
    Example:
    >>> trading_logic = create_trading_logic()
    >>> stop_trade(trading_logic)
    >>> trading_logic['stop_flag']
    True
    """
    trading_logic['stop_flag'] = True

def get_investment(quantity, percent):
    """
    Calculate the investment based on quantity and percentage.
    
    :param quantity: Quantity of the asset.
    :param percent: Percentage of the investment.
    :return: Calculated investment amount.
    
    Example:
    >>> get_investment(100, 10)
    10.0
    >>> get_investment(50, 5)
    2.5

    """
    MINIMAL_INVESTMENT = 6
    investment = quantity * percent / 100
    if investment < MINIMAL_INVESTMENT:
        investment = MINIMAL_INVESTMENT
    return investment