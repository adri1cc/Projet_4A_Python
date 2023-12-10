import ccxt
import dontshare_config as dc
import pandas as pd
from datetime import datetime

# Créer une instance du client Mexc
mexc = ccxt.mexc({
    'apiKey': dc.API_KEY_MEXC,# Clé API publique
    'secret': dc.API_SECRET_MEXC, # Clé API privée
    'enableRateLimit': True,  # Activer la limite de taux si nécessaire
})

mexc_futures = ccxt.mexc({
    'apiKey': dc.API_KEY_MEXC,
    'secret': dc.API_SECRET_MEXC,
    'enableRateLimit': True,  # Activer la limite de taux si nécessaire
    "options": {'defaultType': 'swap' } # Défini comppte FUTURES
})

binance_testnet = ccxt.binance({
    'apiKey': dc.API_KEY_BINANCE,
    'secret': dc.API_SECRET_BINANCE,
    'enableRateLimit': True,  # Activer la limite de taux si nécessaire
})

coinbase_testnet = ccxt.coinbase({
    'apiKey': dc.API_KEY_COINBASE,
    'secret': dc.API_SECRET_COINBASE,
    'enableRateLimit': True,  # Activer la limite de taux si nécessaire
})

exchange = mexc # Choix de l'exchange sur lequel les opérations sont éffectuées
#exchange.set_sandbox_mode(True)  # enable sandbox mode

def getInfoAccount():
    try:
        balance = exchange.fetch_balance()

        # Créer un DataFrame pandas pour stocker les informations du compte
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

        # Afficher le DataFrame
        return df_account

    except ccxt.NetworkError as e:
        print('Problème de connexion : ', type(e).__name__, str(e))
    except ccxt.ExchangeError as e:
        print('Erreur d\'échange : ', type(e).__name__, str(e))
    except Exception as e:
        print('Une erreur s\'est produite : ', type(e).__name__, str(e))
    
def getOHLCV(symbol, timeframe,since: int | None = None,limit: int | None = None):
    
    print("Récupération des données...")
    # Récupérer les bougies
    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        
        # Créer une liste pour stocker les données des bougies
        candle_data = []

        for candle in candles:
            timestamp, open_, high, low, close, volume = candle
            dt_object = datetime.utcfromtimestamp(timestamp / 1000)  # Convertir le timestamp en objet datetime
            candle_data.append([dt_object, open_, high, low, close, volume])

        # Créer un DataFrame pandas
        columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = pd.DataFrame(candle_data, columns=columns)
        print("Données récupérerées")
        # Afficher le DataFrame
        return df

    except ccxt.NetworkError as e:
        print('Problème de connexion : ', type(e).__name__, str(e))
    except ccxt.ExchangeError as e:
        print('Erreur d\'échange : ', type(e).__name__, str(e))
    except Exception as e:
        print('Une erreur s\'est produite : ', type(e).__name__, str(e))

def place_order(symbol="BTC/USDT", direction="short", stop_loss=None, take_profit=None, investment_value=None, limit_price=None):

    # Direction : long or short
    
    # Order parameters
    side = 'buy' if direction == 'long' else 'sell'
    # Create the order
    order_params = {
        'symbol': symbol,
        'side': side,
        'type': 'limit',  # You can adjust the order type according to your needs
        'amount': investment_value,
        'stopPrice': stop_loss,
        'takeProfitPrice': take_profit,
        'price': limit_price,  # Specify the limit price
    }

    try:
        # Place the order
        order = exchange.create_order(**order_params)
        print('Order placed successfully:', order)

    except ccxt.NetworkError as e:
        print('Connection problem: ', type(e).__name__, str(e))
    except ccxt.ExchangeError as e:
        print('Exchange error: ', type(e).__name__, str(e))
    except Exception as e:
        print('An error occurred: ', type(e).__name__, str(e))
    return 


def getQuantity(pair, side):
    balance = getInfoAccount()
    print(balance['Currency'])
    quantity = 0 

    base_currency, quote_currency = pair.split("/")
    
    if side == "sell":

        if base_currency not in balance['Currency'].values:
            print(f"{base_currency} not found in the balance.")
            return 0
        
        quantity = balance['Free'][balance['Currency'] == base_currency].values[0]
        print(f"Quantity of {base_currency} for {side}: {quantity}")

    elif side == "buy":

        if quote_currency not in balance['Currency'].values:
            print(f"{quote_currency} not found in the balance.")
            return 0
        
        quantity = balance['Free'][balance['Currency'] == quote_currency].values[0]
        print(f"Quantity of {quote_currency} for {side}: {quantity}")

    return quantity

import os

def getHistoricalData(pair, timeframe, since):
    # format for since '2022-07-21 00:00:00'
    from_ts = exchange.parse8601(since)
    ohlcv_list = []
    ohlcv = exchange.fetch_ohlcv(pair, timeframe, since=from_ts, limit=1000)
    ohlcv_list.append(ohlcv)
    while True:
        from_ts = ohlcv[-1][0]
        new_ohlcv = exchange.fetch_ohlcv(pair, timeframe, since=from_ts, limit=1000)
        ohlcv.extend(new_ohlcv)
        if len(new_ohlcv) != 1000:
            break
    df = pd.DataFrame(ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df.set_index('date', inplace=True)
    df = df.sort_index(ascending=True)
    
    # Replace '/' character with '_'
    pair_dir = pair.replace('/', '_')

    # Generate output directory based on pair and timeframe
    output_dir = f"{pair_dir}_{timeframe}_data"
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename based on pair, timeframe, and start date
    output_filename = os.path.join(output_dir, f"{pair_dir}_{timeframe}_{since.replace(':', '-')}.csv")

    # Save DataFrame to CSV file
    df.to_csv(output_filename)

# Example usage:
getHistoricalData('BTC/USDT', '5m', '2022-07-21 00:00:00')

