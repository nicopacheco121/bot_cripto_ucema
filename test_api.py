# import requests
#
# api_url = "https://testnet.binance.vision/api/v3/ticker/price"
# response = requests.get(api_url)
# prices = response.json()
# print(prices)

from binance.client import Client
import keys

# Reemplaza 'tu_api_key' y 'tu_api_secret' con tus claves de testnet
api_key = keys.API_KEY
api_secret = keys.API_SECRET

# Crea una instancia del cliente de Binance
client = Client(api_key, api_secret, testnet=True)

try:
    # Obtener precios de todos los símbolos
    prices = client.get_all_tickers()
    print(prices)
except Exception as e:
    print("Error al realizar la solicitud:", e)