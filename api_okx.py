"""
Módulo para interactuar con la API de OKX
Este módulo proporciona funciones para interactuar con la API de OKX,
incluyendo operaciones de cuenta, trading y obtención de datos de mercado.

Utilizaremos la libreria python-okx.

Para usar este módulo, es necesario registrarse en OKX y obtener las credenciales de API:
1. Regístrate en OKX: (pueden usar este link para obtener un 20% de cashback en las operaciones)
https://www.okx.com/join/UCEMA2024
2. Login OKX → Trade → Demo Trading → Personal Center → Demo Trading API → Create Demo Trading V5 API Key → Start your Demo Trading

Documentación de la librería: https://github.com/okxapi/python-okx

Lo que haremos con la api es:
- Obtener balance
- Obtener posiciones abiertas
- Descargar precios
- Consultar y Setear leverage
- Consultar contratos (tamaño posicion)
- Abrir una posicion == Enviar una orden market
- Consultar una orden
- Cerrar una posicion (enviar client_order_id)

"""
import time
import datetime
import uuid
import base64
import pandas as pd
import pprint  # import print para poder imprimir los json de manera mas ordenada

# Usaremos la libreria okx para interactuar con la api de okx
from okx.Account import AccountAPI
import okx.MarketData as MarketData
from okx.Trade import TradeAPI

# Importar las claves de API desde un archivo separado por seguridad
from keys import API_KEY, API_SECRET, PASSPHRASE


# Configuración de la API
def get_account_api(api_key, api_secret, passphrase, flag='1'):
    """Inicializa y retorna una instancia de AccountAPI."""
    # flag = "1"  # live trading: 0, demo trading: 1
    return AccountAPI(api_key, api_secret, passphrase, flag=flag, debug=False)


def get_account_md_api(flag='1'):
    """Inicializa y retorna una instancia de MarketAPI."""
    return MarketData.MarketAPI(flag=flag, debug=False)


def get_account_trade_api(api_key, api_secret, passphrase, flag='1'):
    """Inicializa y retorna una instancia de TradeAPI."""
    return TradeAPI(api_key, api_secret, passphrase, flag=flag, debug=False)


# Funciones de utilidad
def generate_unique_clordid():
    """Genera un ID de orden único de 32 caracteres alfanuméricos."""
    uuid_value = uuid.uuid4()

    # Convertir el UUID a bytes y luego a base64
    uuid_bytes = uuid_value.bytes
    base64_uuid = base64.b64encode(uuid_bytes).decode('ascii')

    # Eliminar caracteres no alfanuméricos y limitar a 32 caracteres
    clean_id = ''.join(c for c in base64_uuid if c.isalnum())[:32]

    return clean_id


# Funciones para interactuar con la api de okx
def get_instruments(account_api, instType='SWAP'):
    """
    https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-instruments
    Obtiene información sobre los instrumentos disponibles.

    :param account_api: Instancia de AccountAPI
    :param instType: Tipo de instrumento (por defecto SWAP)
    :return: Lista de instrumentos
    """

    instruments = account_api.get_instruments(instType=instType)
    return instruments.get('data', [])


def get_data_instruments(account_api, tickers, instType='SWAP'):
    """
    Obtiene datos específicos de los instrumentos seleccionados.

    Comentarios sobre el size
    En OKX el size de la orden no es una cantidad de usdt ni tampoco una cantidad de cripto, sino que es
    una cantidad de contratos. Por ello, debermos calcular cuantos contratos vamos a comprar o vender.

    Detalles a tener en cuenta:
    - ctVal: Contract value, es el valor de un contrato en usd. Por ejemplo, en BTC-USDT-SWAP es 0.001
    - minSz: Minimum size, es el minimo size que se puede enviar en una orden. Por ejemplo, en BTC-USDT-SWAP es 0.1
    - 'lotSz': size del lote, es el incremento minimo que se puede enviar en una orden. Por ejemplo, en BTC-USDT-SWAP es 0.1

    Valor del contrato = ctVal * precio del activo
    Cantidad de contratos = Margen * Leverage / Valor del contrato
    Luego ajustamos el size por el 'lotSz'

    Entonces, si queremos enviar una orden de 100 usdt de margen con leverage 1 en BTC-USDT-SWAP, a un precio del
    activo de 60.000 USDT, debemos calcular el size de la siguiente manera:

    Valor del contrato = 0.001 * 60.000 = 60 USDT
    Size = 100 * 1 / 60 = 1.6666666666666667
    Size ajustado por el 'lotSz' = 1.6

    https://www.okx.com/es-es/trade-market/info/swap

    :param account_api: Instancia de AccountAPI
    :param tickers: Lista de tickers de interés
    :param instType: Tipo de instrumento (por defecto SWAP)
    :return: Diccionario con datos de los instrumentos
    """

    instruments = get_instruments(account_api=account_api, instType=instType)

    data = {}
    for i in instruments:
        if i['instId'] in tickers:
            data[i['instId']] = {
                'instId': i['instId'],
                'ctVal': float(i['ctVal']),
                'minSz': float(i['minSz']),
                'lotSz': float(i['lotSz'])
            }  # generamos el diccionario con los datos de los instrumentos

    # podriamos tambien entregar el max leverage, etc...

    return data


def set_leverage(account_api, instId, lever, mgnMode='isolated'):
    """
    https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-leverage

    Establece el apalancamiento para un instrumento.

    :param account_api: Instancia de AccountAPI
    :param instId: ID del instrumento
    :param lever: Nivel de apalancamiento
    :param mgnMode: Modo de margen (por defecto 'isolated')
    :return: True si se estableció correctamente, False en caso contrario
    """

    lever = str(lever)

    # Primero consultamos el leverage, y en caso necesario lo modificamos
    lever_actual = account_api.get_leverage(instId=instId, mgnMode=mgnMode)
    lever_actual = lever_actual.get('data', [])
    for i in lever_actual:

        lever_side = i['lever']
        if lever != lever_side:
            data = account_api.set_leverage(instId=instId, lever=lever, mgnMode=mgnMode, posSide=i['posSide'])

            if data['code'] != '0':
                return False

    return True


def get_balance(account_api):
    """
    https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-balance

    Obtiene el balance de la cuenta.

    :param account_api: Instancia de AccountAPI
    :return: Diccionario con los balances por moneda
    """
    result = account_api.get_account_balance()

    balance = {}
    for i in result['data'][0]['details']:
        coin = i['ccy']
        monto = i['availBal']
        balance[coin] = monto

    return balance


def get_usdt_balance(account_api):
    """
    Obtiene el balance de USDT.

    :param account_api: Instancia de AccountAPI
    :return: Balance de USDT como float
    """

    balance = get_balance(account_api)
    return float(balance.get('USDT', 0))


def get_positions(account_api, instType='SWAP'):
    """
    https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-positions

    Obtiene las posiciones abiertas.

    :param account_api: Instancia de AccountAPI
    :param instType: Tipo de instrumento (por defecto SWAP)
    :return: Lista de posiciones abiertas
    """
    positions = account_api.get_positions(instType=instType)
    return positions.get('data', [])


def get_positions_dict(account_api, instType='SWAP'):
    """
    https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-positions

    Obtiene las posiciones abiertas en un diccionario con el instId como clave.

    :param account_api: Instancia de AccountAPI
    :param instType: Tipo de instrumento (por defecto SWAP)
    :return: Diccionario de posiciones abiertas
    """
    data = get_positions(account_api=account_api, instType=instType)

    positions_dict = {}
    for i in data:
        positions_dict[i['instId']] = {
            'posSide': i['posSide'],
            'avgPx': float(i['avgPx']),
            'markPx': float(i['markPx']),
            'fee': float(i['fee']),
            'lever': float(i['lever']),
            'margin': float(i['margin']),
            'notionalUsd': float(i['notionalUsd'])
        }

    return positions_dict


def get_historical_prices(client_md, instId, bar='1m', limit=300):
    """
    https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks

    Obtiene los precios históricos de un instrumento.

    :param client_md: Instancia de MarketDataAPI
    :param instId: ID del instrumento
    :param bar: Intervalo de tiempo (por defecto '1m')
    :param limit: Cantidad de datos a obtener (por defecto 300)
    :return: DataFrame con los precios históricos
    """
    data = client_md.get_candlesticks(instId, bar=bar, limit=limit)
    return pd.DataFrame(data.get('data', []))


def get_historical_data_formatted(client_md, instId, bar='1m', limit=300):
    """
    https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks

    Obtiene y formatea datos históricos de precios.

    :param client_md: Instancia de MarketAPI
    :param instId: ID del instrumento
    :param bar: Intervalo de tiempo (por defecto '1m')
    :param limit: Número de velas a obtener (por defecto 300)
    :return: DataFrame con los datos históricos formateados
    """

    df = get_historical_prices(client_md, instId, bar=bar, limit=limit)

    if not df.empty:

        columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
        df.columns = columns  # renombro las columnas
        df = df.astype(float)  # convierto a float

        df['time'] = pd.to_datetime(df['time'], unit='ms')  # convierto el tiempo a datetime
        df.set_index('time', inplace=True)
        df.sort_index(inplace=True)  # ordeno el index por fecha

        # elimino la vela no confirmada, es decir, la que es 0
        df = df[df['confirm'] == 1]

    return df


def send_market_order(account_trade_api, instId, tdMode, ccy, clOrdId, side, posSide, ordType, sz):
    """
    https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order

    Envía una orden de mercado.

    :param account_trade_api: Instancia de TradeAPI
    :param instId: ID del instrumento
    :param tdMode: Modo de trading (cross o isolated)
    :param ccy: Moneda de la orden
    :param clOrdId: ID de la orden
    :param side: Lado de la orden (buy o sell)
    :param posSide: Lado de la posición (long o short)
    :param ordType: Tipo de orden (market)
    :param sz: Tamaño de la orden
    :return: Respuesta de la API
    """
    return account_trade_api.place_order(
        instId=instId,
        tdMode=tdMode,
        ccy=ccy,
        clOrdId=clOrdId,
        side=side,
        posSide=posSide,
        ordType=ordType,
        sz=sz
    )


def api_open_position(instId, posSide, sz, account_trade_api):
    """
    Abre una nueva posicion

    :param instId: ID del instrumento
    :param posSide: Lado de la posición ('long' o 'short')
    :param sz: Tamaño de la orden
    :param account_trade_api: Instancia de TradeAPI
    :return: Tupla con el ID de la orden y el código de respuesta
    """

    clOrdId = generate_unique_clordid()

    order = send_market_order(account_trade_api=account_trade_api,
                              instId=instId,
                              tdMode='isolated',
                              ccy='USDT',
                              clOrdId=clOrdId,
                              side='buy' if posSide == 'long' else 'sell',
                              posSide=posSide,
                              ordType='market',
                              sz=sz)

    return clOrdId, order.get('code')


def api_close_position(instId, posSide, account_trade_api, clOrdId=None, mgnMode='isolated', ccy='USDT', autoCxl='true'):
    """
    Cierra una posición existente.

    :param instId: ID del instrumento
    :param posSide: Lado de la posición ('long' o 'short')
    :param account_trade_api: Instancia de TradeAPI
    :param clOrdId: ID de orden del cliente (opcional)
    :param mgnMode: Modo de margen (por defecto 'isolated')
    :param ccy: Moneda (por defecto 'USDT')
    :param autoCxl: Cancelación automática (por defecto 'true')
    :return: ID de la orden de cierre
    """

    if not clOrdId:
        clOrdId = generate_unique_clordid()

    account_trade_api.close_positions(
        instId=instId,
        mgnMode=mgnMode,
        posSide=posSide,
        ccy=ccy,
        autoCxl=autoCxl,
        clOrdId=clOrdId
    )
    # en este caso me conviene enviar el clOrdId para luego poder consultar la orden, ya que el cierre de posicion
    # no me devuelve un order id

    return clOrdId


def get_data_order(account_trade_api, instId, clOrdId, close=False):
    """
    Obtiene los detalles de una orden.

    :param close: Caso verdadero tambien devuelve el pnl
    :param account_trade_api: Instancia de TradeAPI
    :param instId: ID del instrumento
    :param clOrdId: ID de la orden
    :return: Diccionario con los datos de la orden
    """
    data = account_trade_api.get_order(instId=instId, clOrdId=clOrdId)
    data = data.get('data', [])

    if not data:  # si no hay data, espero 1 segundo y vuelvo a consultar
        time.sleep(1)
        data = account_trade_api.get_order(instId=instId, clOrdId=clOrdId)
        data = data.get('data', [])

    data = data[0]

    r = {}

    if data:
        execution_time = data['fillTime']
        # execution time from timestamp to datetime to string
        execution_time = datetime.datetime.fromtimestamp(int(execution_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')
        r['execution_time'] = execution_time
        r['avg_price'] = float(data['avgPx'])
        r['contratos'] = float(data['sz'])
        r['fee'] = float(data['fee'])

        if close:
            r['pnl'] = float(data['pnl'])

    return r


def get_data_open_position(account_trade_api, instId, clOrdId):
    """
    Retorna el execution_time, avx_price, fillSz, fee

    :param account_trade_api: Instancia de TradeAPI
    :param instId: ID del instrumento
    :param clOrdId: ID de la orden
    :return: Diccionario con los datos de la orden
    """
    return get_data_order(account_trade_api, instId, clOrdId)


def get_data_close_position(account_trade_api, instId, clOrdId):
    """
    Retorna el execution_time, avx_price, fee, pnl

    :param account_trade_api: Instancia de TradeAPI
    :param instId: ID del instrumento
    :param clOrdId: ID de la orden
    :return: Diccionario con los datos de la orden
    """

    return get_data_order(account_trade_api, instId, clOrdId, close=True)


# Ejemplo de uso
if __name__ == '__main__':

    account_api = get_account_api(API_KEY, API_SECRET, PASSPHRASE)  # Ir a los metodos de account api para mostrar
    account_trade_api = get_account_trade_api(API_KEY, API_SECRET, PASSPHRASE)
    client_md = get_account_md_api()

    """ BALANCE """
    balance = get_balance(account_api)
    print(balance)

    usdt = get_usdt_balance(account_api)
    print(usdt)

    """ POSICIONES ABIERTAS """
    instType = 'SWAP'  # SWAP es para futuros perpetuos, tambien puede ser SPOT, etc
    # previo abrir una posicion para ver algo
    posiciones = get_positions(account_api=account_api, instType=instType)
    print(posiciones)

    # Ver detalle en ejemplo_order.py

    dict_positions = get_positions_dict(account_api=account_api, instType=instType)
    pprint.pprint(dict_positions)

    """ DATA DE INSTRUMENTOS Y LEVERAGE """
    # Instruments
    tickers = ['BTC-USDT-SWAP', 'ETH-USDT-SWAP']
    instruments = get_data_instruments(account_api, tickers)
    print(instruments)

    # Setear leverage
    instId = 'BTC-USDT-SWAP'
    lever = 5
    print(set_leverage(account_api, instId, lever))

    """ PRECIOS """
    instId = "BTC-USDT-SWAP"

    # Traigo los precios de BTC-USDT-SWAP
    data = client_md.get_candlesticks('BTC-USDT-SWAP', bar='1m', limit=300)
    data = data.get('data', [])
    df = pd.DataFrame(data)
    print(df)

    # Ahora usando las funciones que formatean los datos
    df = get_historical_data_formatted(client_md, instId, bar='1m', limit=300)

    print(df)
    print(df.columns)

    """ ORDENES """
    # # Descomentar para probar las ordenes
    # # Creo una orden
    # order = account_trade_api.place_order(instId='BTC-USDT-SWAP',
    #                                       tdMode='isolated',  # cross es para margen cruzado, isolated es para margen aislado
    #                                       ccy='USDT',  # moneda de la orden
    #                                       clOrdId='test',  # id de la orden
    #                                       side='buy',  # buy o sell
    #                                       posSide='long',  # long o short
    #                                       ordType='market',
    #                                       sz='1')
    #
    # print(order)
    # # la diferencia entre cross e isolated es que en cross se usa el total del balance para la operacion, en isolated se usa un margen aislado
    #
    # order_id = order['data'][0]['ordId']
    #
    # # Consultar una orden
    # order = account_trade_api.get_order(instId='BTC-USDT-SWAP', ordId=order_id)
    # pprint.pprint(order)
    # # Ver detalle en ejemplo_order.py
    #
    # # Cerrar una posicion
    # order = account_trade_api.close_positions(instId='BTC-USDT-SWAP',
    #                                           mgnMode='isolated',
    #                                           posSide='long',
    #                                           ccy='USDT',
    #                                           autoCxl='true',
    #                                           clOrdId='test123')
    # # en este caso me conviene enviar el clOrdId para luego poder consultar la orden, ya que el cierre de posicion
    # # no me devuelve un order id
    # print(order)
    #
    # # Consulto posicion cerrada
    # client_order_id = 'test123'
    # order = account_trade_api.get_order(instId='BTC-USDT-SWAP', clOrdId=client_order_id)
    # pprint.pprint(order)
    #
    # # Ver detalle en ejemplo_order.py

