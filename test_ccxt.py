import ccxt

# Remplacez 'YOUR_API_KEY' et 'YOUR_SECRET' par vos propres clés API Mexc
api_key = 'mx0vglMPbmg3e57ABt'
secret = '71f46bfa8b4a4632860cc3845c262fb7'

# Créer une instance du client Mexc
mexc = ccxt.mexc({
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,  # Activer la limite de taux si nécessaire
})


# binance = ccxt.binance({
#    'apiKey': 'YOUR_TESTNET_API_KEY',
#    'secret': 'YOUR_TESTNET_API_SECRET',
#    'options': {
#        'defaultType': 'future',
#    },
# })

# binance.set_sandbox_mode(True)  # comment if you're not using the testnet
# markets = binance.load_markets()
# binance.verbose = True  # debug output

# balance = binance.fetch_balance()
# positions = balance['info']['positions']
# print(positions)

# Récupérer les détails du compte
try:
    balance = mexc.fetchOHLCV ("BTC/USDT", 1, 1000000, 10)
    print("Solde du compte : ", balance)
except ccxt.NetworkError as e:
    print('Problème de connexion : ', type(e).__name__, str(e))
except ccxt.ExchangeError as e:
    print('Erreur d\'échange : ', type(e).__name__, str(e))
except Exception as e:
    print('Une erreur s\'est produite : ', type(e).__name__, str(e))
