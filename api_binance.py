import requests
from binance import Client
import time
import logging
from math import floor

logging.basicConfig(level=logging.INFO)

import os
from keys import API_KEY, API_SECRET

''"""
https://binance-docs.github.io/apidocs/spot/en/#market-data-endpoints
https://binance-docs.github.io/apidocs/futures/en/#market-data-endpoints


base_point = 'The base endpoint is: https://api.binance.com'
All time and timestamp related fields are in milliseconds.

The base endpoint https://data.binance.com can be used to access the following API endpoints that have NONE as security type:
GET /api/v3/aggTrades
GET /api/v3/avgPrice
GET /api/v3/depth
GET /api/v3/exchangeInfo
GET /api/v3/klines
GET /api/v3/ping
GET /api/v3/ticker
GET /api/v3/ticker/24hr
GET /api/v3/ticker/bookTicker
GET /api/v3/ticker/price
GET /api/v3/time
GET /api/v3/trades
GET /api/v3/uiKlines

General Info on Limits
The following intervalLetter values for headers:
SECOND => S
MINUTE => M
HOUR => H
DAY => D

/api/v3/exchangeInfo rateLimits array contains objects related to the exchange's RAW_REQUESTS, REQUEST_WEIGHT, and ORDERS rate limits.

The limits on the API are based on the IPs, not the API keys.
requests weight: 1200 por minuto

HTTP 429 return code is used when breaking a request rate limit.


# LEVERAGE
https://www.binance.com/en/futures/trading-rules/perpetual/leverage-margin
initialLeverage = leverage max de ese nivel
notionalCap = maximo de la posicion
maintMarginRatio = margen de mantenimiento
Si se va a operar el capital total, se opera un 10% menos de la posicion maxima por las dudas

"""


def get_client(api_key, api_secret, testnet=False):
    """
    Devuelve el cliente de binance

    :return:
    """

    client = Client(api_key, api_secret, testnet=testnet)
    return client

#
# def download_data_spot(symbol, interval, start_time=None, end_time=None, limit=1000):
#     """
#         [
#       [
#         1499040000000,      // Kline open time
#         "0.01634790",       // Open price
#         "0.80000000",       // High price
#         "0.01575800",       // Low price
#         "0.01577100",       // Close price
#         "148976.11427815",  // Volume
#         1499644799999,      // Kline close time
#         "2434.19055334",    // Quote asset volume
#         308,                // Number of trades
#         "1756.87402397",    // Taker buy base asset volume
#         "28.46694368",      // Taker buy quote asset volume
#         "0"                 // Unused field. Ignore.
#       ]
#     ]
#     :param symbol:
#     :param interval:
#     :param start_time:
#     :param end_time:
#     :param limit:
#     :return:
#     """
#     url = '/api/v3/klines'
#
#     if start_time:
#
#         if end_time:
#             params = {'symbol': symbol, 'interval': interval,
#                       'startTime': start_time, 'endTime': end_time,
#                       'limit': limit}
#         else:
#             params = {'symbol': symbol, 'interval': interval,
#                       'startTime': start_time,
#                       'limit': limit}
#
#     else:
#         params = {'symbol': symbol, 'interval': interval, 'limit': limit}
#
#     r = requests.get('https://api.binance.com' + url, params=params)
#
#     js = r.json()
#     return js
#
#
# def download_data_perp(symbol, interval, start_time=None, end_time=None, limit=1000):
#     """
#         [
#           [
#             1499040000000,      // Open time
#             "0.01634790",       // Open
#             "0.80000000",       // High
#             "0.01575800",       // Low
#             "0.01577100",       // Close
#             "148976.11427815",  // Volume
#             1499644799999,      // Close time
#             "2434.19055334",    // Quote asset volume
#             308,                // Number of trades
#             "1756.87402397",    // Taker buy base asset volume
#             "28.46694368",      // Taker buy quote asset volume
#             "17928899.62484339" // Ignore.
#           ]
#         ]
#     :param symbol:
#     :param interval:
#     :param start_time:
#     :param end_time:
#     :param limit:
#     :return:
#     """
#     url = '/fapi/v1/klines'
#
#     if start_time:
#
#         if end_time:
#             params = {'symbol': symbol, 'interval': interval,
#                       'startTime': start_time, 'endTime': end_time,
#                       'limit': limit}
#         else:
#             params = {'symbol': symbol, 'interval': interval,
#                       'startTime': start_time,
#                       'limit': limit}
#
#     else:
#         params = {'symbol': symbol, 'interval': interval, 'limit': limit}
#
#     r = requests.get('https://fapi.binance.com' + url, params=params)
#
#     js = r.json()
#     return js
#
#
# """
# FUNCIONES PARA TRABAJAR CON BINANCE
#
# - X consultar en billetera PERPETUO BUSD
# - X consultar POSICIONES ABIERTAS
# - X RUTEO orden PERPETUO - OJO CON EL TICK SIZE
# - X CONSULTAR orden perpetuo
# - X CERRAR POSICION PERPETUO
# - X CERRAR PARCIAL POSICION PERPETUO - TENER EN CUENTA EL TICK SIZE
# - X VER EL TICK SIZE DEL INSTRUMENTO
# - X OPEN POSITION
#
# - X CONSULTAR SI EL TICKER ESTA EN PERPETUO
# - X CONSULTAR LA PALANCA DEL TICKER
# - X SETEAR PALANCA Y MARGIN
#
# """
#
# def perp_balance():
#     """
#     Trae el balance available de la cuenta de derivados
#
#     :return: [{'asset': 'USDT', 'balance_available': '50.02781136'}]
#     """
#
#     client = Client(API_KEY, SECRET_KEY)
#     data = client.futures_account_balance()
#     balance = []
#     for i in data:
#         if float(i['balance']) > 0:
#             balance.append({'asset': i['asset'], 'balance_available': i['maxWithdrawAmount']})
#
#     return balance
#
#
# def perp_balance_total(symbol='USDT'):
#     """
#     Trae el balance total de la cuenta de derivados
#
#     :return: [{'asset': 'USDT', 'balance': '50.02781136'}]
#     """
#
#     client = Client(API_KEY, SECRET_KEY)
#     data = client.futures_account_balance()
#
#     for i in data:
#         if i['asset'] == symbol:
#             return float(i['balance'])
#
#
# def spot_balance():
#     """
#     Trae el balance available de la cuenta de spot
#
#     :return:
#     """
#     client = Client(API_KEY, SECRET_KEY)
#     data = client.get_account()
#
#     balance = []
#     if data.get('balances'):
#         for i in data['balances']:
#             if float(i['free']) > 0:
#                 balance.append(i)
#
#     return balance
#
#

#
#
# def ruteo_order(quantity: (float), side: str, reduce_only=None, symbol='ETHUSDT',
#                 type='MARKET'):
#     """
#     Ruta la orden a la plataforma
#
#     quantity: cantidad de la orden
#     side: side de la orden, para open long BUY, para open short SELL, para close long SELL, para close short BUY
#     reduce_only: si es true, la orden solo se ejecuta si reduce la posicion
#     symbol: simbolo de la orden, por ej ETHUSDT
#     type: tipo de orden, por ej MARKET, LIMIT, STOP_MARKET, STOP_LIMIT, TAKE_PROFIT_MARKET, TAKE_PROFIT_LIMIT,
#     TRAILING_STOP_MARKET, TRAILING_STOP_LIMIT
#
#     :return: data de la orden
#     """
#
#     logging.info(
#         f'Orden a ruteo: {symbol}, quantity: {quantity}, side: {side}, type: {type}, reduce_only:{reduce_only}')
#     client = Client(API_KEY, SECRET_KEY)
#     data = client.futures_create_order(symbol=symbol,
#                                        side=side,
#                                        type=type,
#                                        quantity=quantity,
#                                        reduceOnly=reduce_only,
#                                        )
#     return data
#
#
# def consulto_order(order_id, symbol='ETHUSDT'):
#     """
#     Consulto la orden, si falla la consulta tiene 3 intentos mas, duerme 5 segundos en cada intento.
#     Si el error es APIError(code=-2013): Order does not exist. devuelve el error, si no devuelve False
#     :return:
#     """
#
#     client = Client(API_KEY, SECRET_KEY)
#     data = False
#
#     intentos = 0
#     while intentos < 4:
#
#         try:
#             data = client.futures_get_order(symbol=symbol, orderId=order_id)
#             return data
#
#         except Exception as e:
#
#             intentos += 1
#             logging.error(f'Error al consultar la orden {order_id}, consulto en 5 segundos')
#
#             if str(e) == 'APIError(code=-2013): Order does not exist.':
#                 data = 'APIError(code=-2013): Order does not exist.'
#
#             else:
#                 data = False
#
#             time.sleep(5)
#
#     return data
#
#
def get_positions(client):
    """
    Consulto las posiciones abiertas
    :return:
    """

    data = client.futures_position_information()

    positions = []

    for i in data:
        if float(i['positionAmt']) > 0 or float(i['positionAmt']) < 0:
            positions.append(i)

    return positions


# def manage_api_error_order(symbol, type_order, quantity_origin=None):
#     """
#     En caso de algun error al abrir o cerrar total o parcial una posicion, verifica que el movimiento se haya hecho.
#     Si se hizo, entrega True, sino, False.
#     :param symbol: ticker, ejemplo BTCUSDT
#     :param quantity_origin: cantidad de la orden
#     :param type_order: OPEN, CLOSE, PARTIAL_CLOSE
#     :return:
#     """
#     # PRIMERO VEO POSICIONES
#     posiciones = get_positions()
#
#     # VERIFICO QUE TENGA POSICIONES ABIERTAS EN EL TICKER
#     open_position = False
#     position = None
#     for i in posiciones:
#         if i['symbol'] == symbol:
#             position = i
#             open_position = True
#
#     if type_order == 'CLOSE' and not open_position:
#         return True
#
#     elif type_order == 'OPEN' and open_position:
#         return True
#
#     elif type_order == 'PARTIAL_CLOSE' and open_position and quantity_origin is not None:
#         if float(position['positionAmt']) != quantity_origin:
#             return True
#
#     return False
#
#
# def close_position(symbol, partial=False, percentage: float = 0.5):
#     """
#     Maneja el cierre de posiciones tanto parcial como total
#
#     :param symbol:
#     :param partial:
#     :param percentage:
#     :return:
#         order fill (ok) /
#         SIN POSICION PREVIA ABIERTA /
#         0 (si quantity a cerrar es cero) /
#         OK CON ERRORES (si se cerro pero dio error la orden) /
#         False (si no se cerro)
#     """
#     # PRIMERO VEO POSICIONES
#     posiciones = get_positions()
#
#     # VERIFICO QUE TENGA POSICIONES ABIERTAS EN EL TICKER
#     open_position = False
#     position = None
#     for i in posiciones:
#         if i['symbol'] == symbol:
#             position = i
#             open_position = True
#
#     if open_position:
#
#         # Verifico si es long o short y pongo el side contrario
#         side = 'SELL' if float(position['positionAmt']) > 0 else 'BUY'
#
#         # Calculo el quantity
#         quantity = adj_quantity(
#             value=abs(float(position['positionAmt'])) * percentage, tick=get_tick_size(symbol=symbol)) if partial else \
#             abs(float(position['positionAmt']))
#
#         # Si la cantidad da 0, no hago nada
#         if quantity == 0:
#             logging.info(f'NO SE PUEDE CERRAR PARCIALMENTE LA POSICION {symbol} PORQUE QUANTITY ES 0')
#             return 0
#
#         # RUTEO LA ORDEN
#         logging.info(f'CIERRO POSICION {symbol}' if not partial else f'CIERRO PARCIAL POSICION {symbol}')
#         data = ruteo_order(
#             quantity=quantity,
#             side=side,
#             reduce_only=True,
#             symbol=symbol,
#             type='MARKET'
#         )
#
#         # TOMO EL ID DE LA ORDEN DE CIERRE ENVIADA
#         order_id = data['orderId']
#
#         # ESPERO PARA QUE SE EJECUTE LA ORDEN
#         time.sleep(3)
#
#         # CONSULTO LA ORDEN
#         data = consulto_order(order_id=order_id, symbol=symbol)
#
#         if data == 'APIError(code=-2013): Order does not exist.':
#             executed_order = manage_api_error_order(
#                 symbol=symbol, quantity_origin=float(position['positionAmt']),
#                 type_order='PARTIAL_CLOSE' if partial else 'CLOSE')
#
#             return 'OK - CON ERRORES' if executed_order else False
#
#         # VERIFICO QUE LA ORDEN SE CIERRE
#         if data.get('status') == 'FILLED':
#             logging.info(
#                 f'POSICION {symbol} CERRADA, avgPrice: {data["avgPrice"]}, executedQty: {data["executedQty"]} ')
#             return data
#
#         else:
#             logging.info(f'POSICION {symbol} NO SE CERRO')
#             return False
#
#     else:
#         logging.info(f'NO HAY POSICIONES ABIERTAS EN {symbol}')
#         return 'SIN POSICION PREVIA ABIERTA'
#
#
# # def close_partial_position(symbol='ETHUSDT', percentage: float = 0.5):
# #     """
# #     Cierro parcial la posicion, PARA EL TAKE PROFIT
# #
# #     :return:
# #     """
# #
# #     # PRIMERO VEO POSICIONES
# #     posiciones = get_positions()
# #
# #     # VERIFICO QUE TENGA POSICIONES ABIERTAS EN EL TICKER
# #     open_position = False
# #     position = None
# #     for i in posiciones:
# #         if i['symbol'] == symbol:
# #             position = i
# #             open_position = True
# #
# #     if open_position:
# #
# #         # VERIFICO SI ES LONG O SHORT
# #         if float(position['positionAmt']) > 0:
# #             side = 'SELL'
# #         else:
# #             side = 'BUY'
# #
# #         # Calculo el quantity
# #         quantity = adj_quantity(value=abs(float(position['positionAmt'])) * percentage,
# #                                 tick=get_tick_size(symbol=symbol))
# #
# #         # Si la cantidad da 0, no hago nada
# #         if quantity == 0:
# #             logging.info(f'NO SE PUEDE CERRAR PARCIALMENTE LA POSICION {symbol} PORQUE QUANTITY ES 0')
# #             return 0
# #
# #         # CIERRO LA POSICION
# #         logging.info(f'CIERRO PARCIAL POSICION {symbol}')
# #         data = ruteo_order(
# #             quantity=quantity,
# #             side=side,
# #             reduce_only=True,
# #             symbol=symbol,
# #             type='MARKET'
# #         )
# #
# #     else:
# #         logging.info(f'NO HAY POSICIONES ABIERTAS EN {symbol}')
# #         return None
# #
# #     # TOMO EL ID DE LA ORDEN DE CIERRE ENVIADA
# #     order_id = data['orderId']
# #
# #     # ESPERO PARA QUE SE EJECUTE LA ORDEN
# #     time.sleep(3)
# #
# #     # CONSULTO LA ORDEN
# #     data = consulto_order(order_id=order_id, symbol=symbol)
# #
# #     if not data:
# #         logging.info(f'POSICION {symbol} NO SE CERRO')
# #         return None
# #
# #     # VERIFICO QUE LA ORDEN SE CIERRE
# #     if data['status'] == 'FILLED':
# #         logging.info(f'POSICION CERRADA PARCIALMENTE {symbol} CERRADA  avg_price: {position["entryPrice"]}, '
# #                      f'quantity: {quantity}')
# #         return data
# #
# #     else:
# #         logging.info(f'POSICION {symbol} NO SE CERRO')
# #         return None
#
#
# def get_tickers_futures():
#     """
#     Devuelve los tickers de los futures
#
#     :return:
#     """
#
#     client = Client(API_KEY, SECRET_KEY)
#     data = client.futures_exchange_info()
#
#     tickers = []
#     for i in data['symbols']:
#         tickers.append(i)
#
#     return tickers
#
#
# def get_tick_size(symbol='ETHUSDT'):
#     """
#     Devuelve el tick size del simbolo
#
#     :return:
#     """
#
#     data_futures = get_tickers_futures()
#     data_ticker = [i for i in data_futures if i['symbol'] == symbol]
#     tick_size = data_ticker[0]['filters'][1]['stepSize']
#     return tick_size
#
#
# def get_price(symbol='ETHUSDT'):
#     """
#     Devuelve el precio del simbolo
#     si falla la consulta tiene 3 intentos mas, duerme 5 segundos en cada intento.
#
#     :return:
#     """
#
#     intentos = 0
#
#     while intentos < 4:
#
#         try:
#             client = Client(API_KEY, SECRET_KEY)
#             data = client.futures_symbol_ticker(symbol=symbol)
#             price = float(data['price'])
#             return price
#
#         except Exception as e:
#
#             intentos += 1
#             logging.error(f'Error al consultar el precio de {symbol}, consulto en 5 segundos')
#             logging.error(e)
#             time.sleep(5)
#
#     raise Exception(f'Error al consultar el precio de {symbol}')
#
#
#
#
# def adj_quantity(value, tick):
#     """
#     Ajusta la cantidad de acuerdo al tick size SIEMPRE hacia el piso
#
#     :param value: cantidad a operar previo al ajuste
#     :param tick: tick size del ticker
#     :return: cantidad ajustada para operar
#     """
#
#     tick = float(tick)
#
#     if tick < 1:
#
#         output = "{:.7f}".format(tick)
#         tick = output.rstrip('0').rstrip('.') if '.' in output else output
#         decimal_places = len(tick.split('.')[1])
#         end_in_five = tick[-1] == '5'
#
#         multiplier = 10 ** decimal_places
#
#         value = round(floor(value * multiplier) / multiplier, decimal_places)
#
#     else:
#         decimal_places = 0
#         end_in_five = False
#         multiplier = 1
#         value = round(floor(value), 0)
#
#     value_return = round(value, decimal_places)
#
#     if end_in_five:
#         adj_func = floor
#
#         end_five_multiplier = multiplier / 10
#
#         value = value * end_five_multiplier
#
#         value = (adj_func(value * 2) / 2) / end_five_multiplier
#
#         value_return = round(value, decimal_places)
#
#     return value_return
#
#
# def get_max_leverage(symbol='ETHUSDT'):
#     """
#     Devuelve el maximo leverage permitido para el simbolo
#
#     :return:
#     """
#
#     client = Client(API_KEY, SECRET_KEY)
#     leverage = client.futures_leverage_bracket()
#     leverage_symbol = [i for i in leverage if i['symbol'] == symbol]
#     max_leverage = leverage_symbol[0]['brackets'][0]['initialLeverage']
#
#     return leverage
#
#
# # PODRIA HACERLO DE UNA SIN UNA FUNCION
# def set_leverage(leverage: int, symbol='ETHUSDT'):
#     """
#     Setea el leverage para el simbolo
#
#     :return:
#     """
#
#     client = Client(API_KEY, SECRET_KEY)
#     data = client.futures_change_leverage(symbol=symbol, leverage=leverage)
#
#     return data
#
#
# def set_margin_type(margin_type='ISOLATED', symbol='ETHUSDT'):
#     """
#     Setea el tipo de margen para el simbolo
#
#     :return:
#     """
#
#     data = False
#     client = Client(API_KEY, SECRET_KEY)
#     try:
#         data = client.futures_change_margin_type(symbol=symbol, marginType=margin_type)
#
#     except Exception as e:
#         if str(e) == 'APIError(code=-4046): No need to change margin type.':
#             data = True
#
#     return data
#
#
# def open_position(size: float, side: str, leverage: int, symbol='ETHUSDT'):
#     """
#     size = cantidad de dinero a invertir
#     side = long es BUY short es SELL
#     leverage = apalancamiento
#     symbol = simbolo de la orden, por ej ETHUSDT
#
#     Abro posicion
#     :return:
#     """
#
#     # Calculo el quantity con leverage y tick size
#     # Pido el tick size
#     tick_size = get_tick_size(symbol=symbol)
#     # Pido el price
#     price = get_price(symbol=symbol)
#     # Calculo el quantity ajustado
#     quantity = adj_quantity(size / price * leverage, tick_size)
#
#     if quantity > 0:
#
#         # ABRIR POSICION
#         logging.info(f'ABRO POSICION {symbol}')
#         data = ruteo_order(
#             quantity=quantity,
#             side=side,
#             reduce_only=False,
#             symbol=symbol,
#             type='MARKET'
#         )
#
#         # TOMO EL ID DE LA ORDEN DE CIERRE ENVIADA
#         order_id = data['orderId']
#
#         # ESPERO PARA QUE SE EJECUTE LA ORDEN
#         time.sleep(3)
#
#         # CONSULTO LA ORDEN
#         data = consulto_order(order_id=order_id, symbol=symbol)
#
#         if data == 'APIError(code=-2013): Order does not exist.':
#             executed_order = manage_api_error_order(
#                 symbol=symbol,
#                 type_order='OPEN')
#
#             return 'OK - CON ERRORES' if executed_order else False
#
#         # VERIFICO QUE LA ORDEN SE CIERRE
#         if data.get('status') == 'FILLED':
#             logging.info(f'POSICION {symbol} ABIERTA, avg_price: {data["avgPrice"]}, quantity: {data["executedQty"]}')
#             return data
#
#         else:
#             logging.info(f'POSICION {symbol} NO SE ABRIÓ')
#             return False
#
#     else:
#         logging.info(f'POSICION {symbol} NO SE ABRIÓ POR RESULTAR CANTIDAD 0')
#         return 'CANTIDAD 0'
#
#
# def futures_trades(symbol, limit=1000, from_id=None):
#     """
#
#     Si no fromId, trae los 7 dias mas recientes
#     Maximo limit es 1.000
#
#     :param symbol:
#     :param limit:
#     :param from_id: numero del id del trade desde el que traer la informacion
#     :return:
#     """
#
#     client = Client(API_KEY, SECRET_KEY)
#     data = client.futures_account_trades(symbol=symbol, limit=limit, fromId=from_id)
#     return data
#
#
# def api_binance_ping(api_key, secret_key):
#     """
#     PING
#
#     :return: True
#     """
#
#     try:
#         test_ping = Client(api_key, secret_key)
#         return test_ping.ping()
#
#     except Exception as e:
#         logging.error(f'ERROR PING: {e}')
#         return False
#
#
# def get_pnl_unrealized():
#     """
#     Devuelve la sumatoria de los pnl no realizados de todas las posiciones abiertas
#
#     :return: float
#     """
#
#     posiciones = get_positions()
#     pnl = 0
#     for p in posiciones:
#         pnl += float(p['unRealizedProfit'])
#
#     return pnl
#
#
# def test():
#     client = Client(API_KEY, SECRET_KEY)
#     # KLINES
#     # data = client.futures_klines(symbol='BTCUSDT', interval='1h')
#
#     # QUIZA CON ESTE SE PUEDA VER LA PALANCA MAX
#     # data = client.futures_leverage_bracket(symbol='MKRUSDT')
#     data = ''
#     for i in range(100):
#
#         time.sleep(15)
#
#         data = client.futures_account_balance()
#         for i in data:
#             if float(i['balance']) > 0:
#                 print(i)
#
#         print(data)
#
#     return data
#
# def order_book():
#     client = Client(API_KEY, SECRET_KEY)
#     data = client.futures_order_book(symbol='ETHUSDT')
#     return data


if __name__ == '__main__':

    """
    SI ME DA ERROR EL CONSULTAR ORDEN, deberia ver si cambió algo. Es decir,
    Si fue open, tengo que consultar si se abrió la posicion por XX cantidad
    Si fue close parcial, tengo que consltar si cambió la posicion a menos cantidad de la que tenía
    Si fue close tota, teng que consultar si efectivamente ya no tengo más posición
    
    Si todo esto fue ok, tengo que enviar un telegram que diga
    hubo un error al consultar XXX orden, pero se ejecutó correctamente, por fvor completar en "trades" la posicion
    Y deberia ir al sheet de posiciones y hacer todo como corresponde
    
    
    """


