import requests
import time
import hashlib
import hmac
import json

API_KEY = 'mx0vglMPbmg3e57ABt'
API_SECRET = '71f46bfa8b4a4632860cc3845c262fb7'
API_BASE_URL = 'https://api.mexc.com'

# Function to create the signature for authenticated endpoints
def create_signature(query_string):
    return hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

# Function to make a request to the MEXC API
def make_api_request(method, endpoint, params=None, data=None):
    timestamp = str(int(time.time() * 1000))  # Millisecond timestamp
    headers = {
        'X-MEXC-APIKEY': API_KEY,
        'Content-Type': 'application/json'
    }

    # Construct query string for signature
    query_string = f'timestamp={timestamp}'
    if params:
        query_string += '&' + params

    # Add signature to headers for signed endpoints
    if API_KEY and API_SECRET:
        signature = create_signature(query_string)
        query_string += f'&signature={signature.lower()}'  # Signature in lowercase
        print("query", query_string)
    endpoint = API_BASE_URL + endpoint + '?' + query_string

    if method == 'GET':
        response = requests.get(endpoint, headers=headers)
    elif method == 'POST':
        response = requests.post(endpoint, headers=headers, json=data)
    else:
        raise ValueError("Unsupported method")

    return response

# Example: Getting market data for 'BTC_USD'
symbol = 'BTCUSDT'
market_data = make_api_request('GET', '/api/v3/', f'{symbol}')

if market_data.status_code == 200:
    print('Market Data for BTC_USD:')
    print(json.dumps(market_data.json(), indent=2))
else:
    print('Failed to retrieve market data.')
    print('Status Code:', market_data.status_code)

def test_ping_endpoint():
    try:
        response = requests.get(f"{API_BASE_URL}/api/v3/ping")

        if response.status_code == 200:
            print("API Ping successful!")
        else:
            print(f"Failed to ping the API. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

test_ping_endpoint()

def check_server_time():
    try:
        response = requests.get(f"{API_BASE_URL}/api/v3/time")

        if response.status_code == 200:
            server_time = response.json().get('serverTime')
            print(f"Server Time: {server_time}")
        else:
            print(f"Failed to check server time. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

check_server_time()

def get_default_symbols():
    try:
        response = requests.get(f"{API_BASE_URL}/api/v3/defaultSymbols")

        if response.status_code == 200:
            symbols = response.json().get('data')
            if symbols:
                print("Default Symbols:")
                for symbol in symbols:
                    print(symbol)
            else:
                print("No symbols returned.")
        else:
            print(f"Failed to get default symbols. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

#get_default_symbols()

import requests

API_BASE_URL = 'https://api.mexc.com'

def get_exchange_info():
    try:
        response = requests.get(f"{API_BASE_URL}/api/v3/exchangeInfo")

        if response.status_code == 200:
            exchange_info = response.json()
            if exchange_info:
                print("Exchange Information:")
                print(exchange_info)
            else:
                print("No exchange information returned.")
        else:
            print(f"Failed to get exchange information. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

#get_exchange_info()

def get_trades_data(symbol, limit=10):
    try:
        response = requests.get(f"{API_BASE_URL}/api/v3/trades", params={"symbol": symbol, "limit": limit})

        if response.status_code == 200:
            trades_data = response.json()
            if trades_data:
                print(f"Trades Data for {symbol}:")
                print(trades_data)
            else:
                print(f"No trades data available for {symbol}.")
        else:
            print(f"Failed to get trades data. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

# Example usage: Fetching trades data for symbol 'BTC_USDT' with a limit of 10 trades
#get_trades_data('BTCUSDT', limit=10)

def get_kline_data(symbol, interval='1h', limit=10):
    try:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(f"{API_BASE_URL}/api/v3/klines", params=params)

        if response.status_code == 200:
            kline_data = response.json()
            if kline_data:
                print(f"Kline Data for {symbol} (Interval: {interval}):")
                print(kline_data)
            else:
                print(f"No kline data available for {symbol}.")
        else:
            print(f"Failed to get kline data. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

# Example usage: Fetching Kline data for symbol 'BTC_USDT' with a 1-hour interval and a limit of 10 Klines
get_kline_data('BTCUSDT', interval='1h', limit=10)

def get_agg_trades_data(symbol, limit=10):
    try:
        response = requests.get(f"{API_BASE_URL}/api/v3/aggTrades", params={"symbol": symbol, "limit": limit})

        if response.status_code == 200:
            agg_trades_data = response.json()
            if agg_trades_data:
                print(f"Aggregated Trades Data for {symbol}:")
                print(agg_trades_data)
            else:
                print(f"No aggregated trades data available for {symbol}.")
        else:
            print(f"Failed to get aggregated trades data. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

# Example usage: Fetching aggregated trades data for symbol 'BTC_USDT' with a limit of 10 trades
#get_agg_trades_data('BTCUSDT', limit=10)

def get_24hr_ticker(symbol):
    try:
        response = requests.get(f"{API_BASE_URL}/api/v3/ticker/24hr", params={"symbol": symbol})

        if response.status_code == 200:
            ticker_data = response.json()
            if ticker_data:
                print(f"24-hour Ticker Data for {symbol}:")
                print(ticker_data)
            else:
                print(f"No 24-hour ticker data available for {symbol}.")
        else:
            print(f"Failed to get 24-hour ticker data. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

def place_test_order(symbol, side, quantity, price):
    timestamp = str(int(time.time() * 1000))
    headers = {
        'X-MEXC-APIKEY': API_KEY,
        'Content-Type': 'application/json'
    }

    query_string = f"symbol={symbol}&side={side}&quantity={quantity}&price={price}&type=limit&timeInForce=GTC&timestamp={timestamp}"
    signature = create_signature(query_string)
    query_string += f"&signature={signature.lower()}"
    
    endpoint = f"{API_BASE_URL}/api/v3/order/test"
    data = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "type": "limit",
        "timeInForce": "GTC",
        "timestamp": int(timestamp),
        "signature": signature.lower()
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            print("Test order placed successfully.")
            print(response.json())
        else:
            print(f"Failed to place test order. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

# Example usage: Placing a test order for BTC/USDT buying 1 unit at $50000
place_test_order('BTCUSDT', 'BUY', 1, 50000)


def get_orders(symbol):
    timestamp = str(int(time.time() * 1000))
    headers = {
        'X-MEXC-APIKEY': API_KEY,
        'Content-Type': 'application/json'
    }

    query_string = f"symbol={symbol}&timestamp={timestamp}"
    signature = create_signature(query_string)
    query_string += f"&signature={signature.lower()}"
    
    endpoint = f"{API_BASE_URL}/api/v3/order?{query_string}"

    try:
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            print("Orders retrieved successfully.")
            print(response.json())
        else:
            print(f"Failed to retrieve orders. Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Request Exception: {e}")

# Example usage: Retrieving orders for BTC/USDT
get_orders('BTCUSDT')

import requests

def get_kline_data(symbol, interval):
    endpoint = f"spot@public.kline.v3.api@{symbol}@{interval}"
    response = requests.get(f"https://api.mexc.com/{endpoint}")

    if response.status_code == 200:
        kline_data = response.json()
        print(f"Kline Data for {symbol} ({interval}):")
        print(kline_data)
    else:
        print(f"Failed to get Kline data. Status Code: {response.status_code}")

# Example usage: Fetching Kline data for symbol 'BTCUSDT' with 1-minute intervals
get_kline_data('BTCUSDT', '1m')
