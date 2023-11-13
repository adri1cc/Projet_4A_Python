import sys

# Use a raw string (r"your_string") or escape backslashes (use \\ instead of \)
sys.path.append(r"C:\Users\Paulin\Documents\Etudes\4A\Computer science\Nouveau dossier\Projet_4A_Python")

# Import the library/module
import mexc_spot_v3
import time

hosts = "https://api.mexc.com"
# mexc_key = "your apiKey"
# mexc_secret = "your secretKey"

# Market Data
"""get kline"""
data = mexc_spot_v3.mexc_market(mexc_hosts=hosts)
params = {
    'symbol': 'BTCUSDT', 
    'interval': '5m', 
    'limit': 10
}
response= data.get_kline(params)
print(response)

