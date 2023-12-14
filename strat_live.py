import api
import strategies
import logging

result = None

def create_trading_logic():
    """
    Create a dictionary to hold trading logic parameters.
    """
    return {'stop_flag': False}

def backtest(value, timeframe, pair, strategy, date):
    """
    Perform backtesting using SimpleSMALive strategy.
    
    :param value: Some value.
    :param timeframe: Timeframe for backtesting.
    :param pair: Trading pair for backtesting.
    :return: Figure object for plotting.
    """
    strategies_dict = {
        'SimpleSMA': strategies.SimpleSMALive,
        # Add other strategies here
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
    """
    investment_threshold = 6
    
    strategies_dict = {
        'SimpleSMA': strategies.SimpleSMALive,
        # Add other strategies here
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

                if investment > investment_threshold:
                    logging.info("Launch buy order")
                    # place_order(pair, "buy", 6, "market")
                    strategy_instance.set_live_trade(True)
                else:
                    logging.info("Not enough funds")
        elif result == "sell":
            quantity_sell = api.get_quantity(pair, "sell")

            if quantity_sell > 0:
                logging.info("Launch sell order")
                # place_order(pair, "sell", 6, "market")
                strategy_instance.set_live_trade(False)
            else:
                logging.info("Not enough funds")

    logging.info("Live trading is stopped")
    del strategy_instance
    
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