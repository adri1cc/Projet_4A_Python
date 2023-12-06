import ccxt
import dontshare_config as dc
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go

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

"""binance_testnet = ccxt.binance({
    'apiKey': dc.API_KEY_BINANCE,
    'secret': dc.API_SECRET_BINANCE,
    'enableRateLimit': True,  # Activer la limite de taux si nécessaire
})

coinbase_testnet = ccxt.coinbase({
    'apiKey': dc.API_KEY_COINBASE,
    'secret': dc.API_SECRET_COINBASE,
    'enableRateLimit': True,  # Activer la limite de taux si nécessaire
})"""

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

