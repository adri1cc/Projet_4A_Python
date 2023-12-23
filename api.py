from datetime import datetime
import os
import ccxt
import logging
import dontshare_config as dc
import pandas as pd
import plotly.graph_objects as go

# Create an instance of the Mexc client
mexc = ccxt.mexc({
    'apiKey': dc.API_KEY_MEXC,  # Public API key
    'secret': dc.API_SECRET_MEXC,  # Private API key
    'enableRateLimit': True,
})

# Create an instance of the Mexc FUTURES client
mexc_futures = ccxt.mexc({
    'apiKey': dc.API_KEY_MEXC,
    'secret': dc.API_SECRET_MEXC,
    'enableRateLimit': True,
    "options": {'defaultType': 'swap'}  # Set account type to FUTURES
})

# Create an instance of the Binance client
binance = ccxt.binance({
    'apiKey': dc.API_KEY_BINANCE,
    'secret': dc.API_SECRET_BINANCE,
    'enableRateLimit': True,
})

# Create an instance of the Coinbase client
coinbase = ccxt.coinbase({
    'apiKey': dc.API_KEY_COINBASE,
    'secret': dc.API_SECRET_COINBASE,
    'enableRateLimit': True,
})

# Choose the exchange on which operations are performed
exchange = mexc

def get_info_account():
    """
    Get account information.

    :return: Pandas DataFrame with account information.
    """
    try:
        balance = exchange.fetch_balance()

        account_info = {
            'Currency': [],
            'Total': [],
            'Free': [],
            'Used': [],
        }

        for currency, data in balance['total'].items():
            account_info['Currency'].append(currency)
            account_info['Total'].append(data)
            account_info['Free'].append(balance['free'][currency])
            account_info['Used'].append(balance['used'][currency])

        df_account = pd.DataFrame(account_info)

        return df_account

    except ccxt.NetworkError as e:
        logging.info('Connection problem: ', type(e).__name__, str(e))
    except ccxt.ExchangeError as e:
        logging.info('Exchange error: ', type(e).__name__, str(e))
    except Exception as e:
        logging.info('An error occurred: ', type(e).__name__, str(e))

def plot_info_account(df_account):
     table_trace = go.Table(
     header=dict(values=df_account.columns),
     cells=dict(values=[df_account[col] for col in df_account.columns])
     )
     figure = go.Figure(data =[table_trace])
     return figure

def get_ohlcv(symbol, timeframe, since: int | None = None, limit: int | None = None):
    """
    Get OHLCV data.

    :param symbol: Trading pair symbol.
    :param timeframe: Timeframe for OHLCV data.
    :param since: Timestamp indicating the start time for data retrieval.
    :param limit: Limit the number of data points to retrieve.
    :return: Pandas DataFrame with OHLCV data.
    """
    logging.info("Fetching data...")
    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe, since, limit)

        candle_data = []

        for candle in candles:
            timestamp, open_, high, low, close, volume = candle
            dt_object = datetime.utcfromtimestamp(timestamp / 1000)  # Convert timestamp to datetime object
            candle_data.append([dt_object, open_, high, low, close, volume])

        # Create a pandas DataFrame
        columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = pd.DataFrame(candle_data, columns=columns)
        logging.info("Data retrieved")
        return df

    except ccxt.NetworkError as e:
        logging.info('Connection problem: ', type(e).__name__, str(e))
    except ccxt.ExchangeError as e:
        logging.info('Exchange error: ', type(e).__name__, str(e))
    except Exception as e:
        logging.info('An error occurred: ', type(e).__name__, str(e))

def place_order(symbol="BTC/USDT", direction="short", stop_loss=None, take_profit=None, investment_value=None,
                limit_price=None):
    """
    Place a trading order.

    :param symbol: Trading pair symbol.
    :param direction: Order direction ('long' or 'short').
    :param stop_loss: Stop loss price.
    :param take_profit: Take profit price.
    :param investment_value: Amount to invest.
    :param limit_price: Limit price for the order.
    """
    # Order parameters
    side = 'buy' if direction == 'long' else 'sell'
    # Create the order
    order_params = {
        'symbol': symbol,
        'side': side,
        'type': 'limit',
        'amount': investment_value,
        'stopPrice': stop_loss,
        'takeProfitPrice': take_profit,
        'price': limit_price,
    }

    try:
        # Place the order
        order = exchange.create_order(**order_params)
        logging.info('Order placed successfully:', order)

    except ccxt.NetworkError as e:
        logging.info('Connection problem: ', type(e).__name__, str(e))
    except ccxt.ExchangeError as e:
        logging.info('Exchange error: ', type(e).__name__, str(e))
    except Exception as e:
        logging.info('An error occurred: ', type(e).__name__, str(e))
    return

def get_quantity(pair, side):
    """
    Get the quantity of a currency in the account.

    :param pair: Trading pair symbol.
    :param side: Order direction ('buy' or 'sell').
    :return: Quantity of the currency.
    """
    balance = get_info_account()
    logging.info(balance['Currency'])
    quantity = 0
    base_currency, quote_currency = pair.split("/")

    if side == "sell":

        if base_currency not in balance['Currency'].values:
            logging.info(f"{base_currency} not found in the balance.")
            return 0

        quantity = balance['Free'][balance['Currency'] == base_currency].values[0]
        logging.info(f"Quantity of {base_currency} for {side}: {quantity}")

    elif side == "buy":

        if quote_currency not in balance['Currency'].values:
            logging.info(f"{quote_currency} not found in the balance.")
            return 0

        quantity = balance['Free'][balance['Currency'] == quote_currency].values[0]
        logging.info(f"Quantity of {quote_currency} for {side}: {quantity}")

    return quantity

def get_historical_data(pair, timeframe, since):# TODO add gestion of out of range (missing values)
    """
    Get historical data for backtesting.

    :param pair: Trading pair symbol.
    :param timeframe: Timeframe for historical data.
    :param since: Start date for data retrieval.
    """
    from_ts = exchange.parse8601(since)
    ohlcv_list = []
    ohlcv = exchange.fetch_ohlcv(pair, timeframe, since=from_ts, limit=1000)
    ohlcv_list.append(ohlcv)

    # Download historical values from "since"
    while True:
        logging.info("Downloading...")
        from_ts = ohlcv[-1][0]
        new_ohlcv = exchange.fetch_ohlcv(pair, timeframe, since=from_ts, limit=1000)
        ohlcv.extend(new_ohlcv)

        if len(new_ohlcv) != 1000:
            break

    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index(ascending=True)
    pair_dir = pair.replace('/', '_')

    # Generate output directory based on pair and timeframe
    output_dir = os.path.join(pair_dir + '_data')
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename based on pair, timeframe, and start date
    filename_prefix = f"{pair_dir}_{timeframe}_{since.replace(':', '-').replace(' ', '_')}"
    output_filename = os.path.join(output_dir, f"{filename_prefix}.csv")

    # Save DataFrame to CSV file
    df.to_csv(output_filename)
    return
