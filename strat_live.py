import time

from strategies import SimpleSMA


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

def SimpleSMALive():
    