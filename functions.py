"""
En este archivo juntaremos diversas funciones necesarias para el funcionamiento del robot.
"""

from api_okx import (get_historical_data_formatted, api_close_position, get_data_close_position, api_open_position,
                     get_data_instruments, set_leverage, get_data_open_position)
from alertas import send_telegram_message
from time import sleep
import google_sheets
from math import floor
import time
from datetime import datetime, timedelta
import indicadores
from keys import CHAT_ID_LIST


""" PARA LA ESTRATEGIA DE TRADING """


def get_data_tickers(parametros, client_md):
    """
    Descarga la data de los tickers que se le pasan en parametros
    """
    data = {}
    for i in parametros:
        ticker = i
        timeframe = parametros[i]['timeframe']
        data[ticker] = get_historical_data_formatted(client_md, ticker, timeframe)

    return data


def get_last_price(data):
    return {k: float(v['close'].iloc[-1]) for k, v in data.items()}


def calculate_indicators(data, parametros):
    """
    Calculo los indicadores de los tickers
    """
    for ticker, df in data.items():
        data[ticker] = indicadores.add_indicadores(df, parametros[ticker])

    return data


def fx_set_leverage(account_trade_api, parametros):
    """
    Seteo el leverage de los tickers
    """
    for p in parametros:
        set_leverage(account_trade_api, p, parametros[p]['leverage'])


def should_close_position(posicion, data, ticker):
    """
    Analizamos si debemos cerrar la posicion

    Retorna un booleano y un string con el motivo de cierre
    """

    stop_loss = posicion['stop_loss']
    take_profit = posicion['take_profit']

    last_price = get_last_price(data)
    close = False

    if last_price[ticker] <= stop_loss:
        close = True, 'stop_loss'
    elif last_price[ticker] >= take_profit:
        close = True, 'take_profit'

    return close, None


def should_open_position(data, parametros):
    """
    Analizamos si debemos abrir la posicion.
    Recibe un data con los indicadores y un dict de parametros con los valores de los indicadores


    Para abrir una posicion tomaremos primero el adx, en base a dicho indicador veremos si usamos rsi o cruce.
    El ADX es conocido como el indicador de tendencia, si el ADX es mayor a 20 entonces la tendencia es fuerte y
    podemos usar el cruce de medias exponenciales, si el ADX es menor a 20 entonces la tendencia es débil y usamos
    el RSI.

    Si ADX > 20 -> cruce
        - Si cruce > 0 -> abrimos posicion long
        - Si cruce < 0 -> abrimos posicion short
    Si ADX < 20 -> rsi
        - Si rsi > 50 -> abrimos posicion short
        - Si rsi < 50 -> abrimos posicion long

    """

    # Obtenemos los indicadores de la ultima fila, es decir, los actuales
    adx = data['ADX'].iloc[-1]
    rsi = data['RSI'].iloc[-1]
    cruce = data['cruce'].iloc[-1]

    # Obtenemos los parametros
    adx_limit = parametros['adx']
    rsi_limit = parametros['rsi']

    # Analizamos si debemos abrir la posicion
    open_position = False
    side = None
    motivo = None

    if adx > adx_limit:  # Tendencia fuerte
        motivo = 'cruce'
        if cruce > 0:
            open_position = True
            side = 'long'
        elif cruce < 0:
            open_position = True
            side = 'short'
    elif adx < adx_limit:  # Tendencia debil
        motivo = 'rsi'
        if rsi > rsi_limit:
            open_position = True
            side = 'short'
        elif rsi < rsi_limit:
            open_position = True
            side = 'long'

    return open_position, side, motivo


def close_positions(posiciones, data, account_trade_api, list_alertas, list_sheets):
    """

    Verifica si cierra alguna posicion.
        Caso de cierre:
            Envia la orden
            Consulta la orden
            Guarda en alertas y en sheets. En sheets va a posiciones y en operaciones.

    :param posiciones:
    :return:
    """

    print('Cerrando posiciones')

    posiciones_cerradas = []
    for p in posiciones:
        # Analizo si cierro la posicion
        close_position, motivo = should_close_position(p, data, p['ticker'])

        if close_position:
            # Cierro la posicion
            ticker = p['ticker']
            pos_side = p['side']
            clOrdId = api_close_position(ticker, pos_side, account_trade_api)
            sleep(0.1)  # Espero un poco para que se ejecute correctamente la orden market

            # Consulto la orden
            data_close = get_data_close_position(account_trade_api, ticker, clOrdId)

            data_close['ticker'] = ticker
            data_close['tipo'] = 'close'
            data_close['side'] = pos_side

            print(f'Posicion cerrada {ticker} por {motivo}')

            posiciones_cerradas.append(p['ticker'])
            list_alertas.append(f"Cierro posicion {p['ticker']} por {motivo}")
            list_sheets.append(data_close)

    return posiciones_cerradas


def usdt_available(usdt, margen, ratio=0.99):
    """
    Consulto si me alcanza el dinero para abrir una nueva posicion
    Al balance en usdt lo multiplico por el ratio ya que a veces no se puede abrir una posicion con el 100% del balance
    :param account_api:
    :return:
    """

    if usdt * ratio > margen:
        return True
    else:
        return False


def adj_quantity(value, tick):
    """
    Ajusta la cantidad de acuerdo al tick size SIEMPRE hacia el piso

    :param value: cantidad a operar previo al ajuste
    :param tick: tick size del contrato del ticker
    :return: cantidad ajustada para operar
    """

    tick = float(tick)

    if tick < 1:

        output = "{:.7f}".format(tick)
        tick = output.rstrip('0').rstrip('.') if '.' in output else output
        decimal_places = len(tick.split('.')[1])
        end_in_five = tick[-1] == '5'

        multiplier = 10 ** decimal_places

        value = round(floor(value * multiplier) / multiplier, decimal_places)

    else:
        decimal_places = 0
        end_in_five = False
        multiplier = 1
        value = round(floor(value), 0)

    value_return = round(value, decimal_places)

    if end_in_five:
        adj_func = floor

        end_five_multiplier = multiplier / 10

        value = value * end_five_multiplier

        value = (adj_func(value * 2) / 2) / end_five_multiplier

        value_return = round(value, decimal_places)

    return value_return


def calculate_size(parametros, price):
    """
    En el caso de OKX, el size de la orden no es una cantidad de usdt ni tampoco una cantidad de cripto, si no que es
    una cantidad de contratos. Por ello, debermos calcular cuantos contratos vamos a comprar o vender.

    Lo que tendremos en cuenta es
    - ctVal: Contract value, es el valor de un contrato en usd. Por ejemplo, en BTC-USDT-SWAP es 0.001
    - minSz: Minimum size, es el minimo size que se puede enviar en una orden. Por ejemplo, en BTC-USDT-SWAP es 0.1
    - tickSz: Tick size, es el incremento minimo que se puede enviar en una orden. Por ejemplo, en BTC-USDT-SWAP es 0.1

    Valor del contrato = ctVal * precio del activo
    Cantidad de contratos = Margen * Leverage / Valor del contrato
    Luego ajustamos el size por el tick size

    Entonces, si queremos enviar una orden de 100 usdt de margen con leverage 1 en BTC-USDT-SWAP, a un precio del
    activo de 60.000 USDT, debemos calcular el size de la siguiente manera:

    Valor del contrato = 0.001 * 60.000 = 60 USDT
    Size = 100 * 1 / 60 = 1.6666666666666667
    Size ajustado por el tick size = 1.6

    Por ultimo, si el size es menor al minSz, entonces no se puede enviar la orden.

    https://www.okx.com/es-es/trade-market/info/swap

    En base al multiplicador, margen y leverage calculamos la cantidad de contratos.
    La cantidad final se ajusta segun el tick size del ticker

    :param parametros:
    :param margen:
    :param leverage:
    :return:
    """

    ctVal = parametros['ctVal']
    margen = parametros['margen']
    leverage = parametros['leverage']

    # Calculo el valor del contrato
    contract_value = ctVal * price

    # Calculo la cantidad de contratos
    quantity = margen * leverage / contract_value

    # Ajusto la cantidad de contratos
    quantity = adj_quantity(quantity, parametros['tickSz'])

    # Si la cantidad de contratos es menor al minSz, devuelvo 0
    if quantity < parametros['minSz']:
        return 0

    return quantity


def open_positions(parametros, posiciones, posiciones_cerradas, usdt, data, account_trade_api, list_alertas, list_sheets):
    """
    Funcion para abrir nuevas posiciones.

    - Tengo en cuenta los parametros
    - Verifico si no esta en posiciones abiertas
    - Verifico si no esta en posiciones cerradas (para no abrir una posicion que acabo de cerrar)
    - Veo si me alcanza el dinero en base al margen y leverage
    - Analizo si abro la posicion, caso positivo:
        calculo el tamaño
        envio la orden
        consulto la orden
        calculo tp y sl
        guardo en alertas
        guardo en sheets (posiciones y en operaciones)

        disminuyo el usdt disponible

    :return:
    """

    tickers_abiertos = [p['ticker'] for p in posiciones]
    last_price = get_last_price(data)

    for p in parametros:
        ticker = p

        # No abro si acaba de cerrar o si esta abierto
        if ticker in posiciones_cerradas or ticker in tickers_abiertos:
            continue

        # Analizo si me alcanza el dinero
        usdt_ok = usdt_available(usdt, parametros[p]['margen'])
        if not usdt_ok:
            print(f"No alcanza el dinero para abrir {ticker}, margen {parametros[p]['margen']}")
            list_alertas.append(f"No alcanza el dinero para abrir {ticker}, margen {parametros[p]['margen']}")
            continue

        # Analizo si abro la posicion
        open_position, side, motivo = should_open_position(data=data[parametros[p]['ticker']], parametros=parametros[p])

        if open_position:

            price = last_price[ticker]

            # Calculo el tamaño
            quantity = calculate_size(parametros[p], price)

            # Abro la posicion
            ticker = parametros[p]['ticker']

            print(f"Abriendo posicion {ticker} por {motivo} side {side} con {quantity} contratos")

            clOrdId = api_open_position(ticker, side, quantity, account_trade_api)
            sleep(1)

            # Consulto la orden
            data_open = get_data_open_position(account_trade_api, ticker, clOrdId)

            # Calculo el take profit y stop loss
            parametros_tp = parametros[p]['take_profit']
            parametros_sl = parametros[p]['stop_loss']

            if side == 'long':
                tp = data_open['avg_price'] * (1 + parametros_tp)
                sl = data_open['avg_price'] * (1 - parametros_sl)
            else:
                tp = data_open['avg_price'] * (1 - parametros_tp)
                sl = data_open['avg_price'] * (1 + parametros_sl)

            data_open['ticker'] = ticker
            data_open['tipo'] = 'open'
            data_open['side'] = side
            data_open['tp'] = tp
            data_open['sl'] = sl
            data_open['margen'] = VOY ACA

            print(f"Posicion abierta {ticker} por {motivo} side {side} con {quantity} contratos")

            list_alertas.append(f"Abro posicion {ticker} por {motivo} side {side}")
            list_sheets.append(data_open)

            # Disminuyo el usdt disponible
            usdt -= parametros[p]['margen']


""" OTROS """


def get_parametros(account_api, sheet, hoja_parametros):
    """
    Obtenemos los parametros de la hoja de google sheets y le agrego ciertas cosas de los instruments

    """
    parametros = google_sheets.read_all_sheet(sheet, hoja_parametros)
    parametros_dict = {p['ticker']: p for p in parametros}

    instruments = get_data_instruments(account_api, tickers=parametros_dict.keys())

    parametros_final = {}

    for key in parametros_dict.keys():
        # Combinar los diccionarios internos
        parametros_final[key] = {**parametros_dict[key], **instruments[key]}
        # en esta linea usamos el desempaquetado de diccionarios de python
        """
        **parametros_dict[key]: El operador ** desempaqueta el diccionario que está en parametros_dict[key]. 
        Esto significa que toma todos los pares clave-valor de ese diccionario y los coloca en el nuevo diccionario que estamos creando.
        el **instruments[key] hace lo mismo, pero con el diccionario instruments[key]
        Luego se combinan ambos diccionarios en uno solo con {**parametros_dict[key], **instruments[key]}
        """

    return parametros_final


def send_telegram_messages(list_alertas, bot_token, chat_id_list):
    """
    Envio los mensajes a telegram
    """
    for alerta in list_alertas:
        send_telegram_message(bot_token, alerta, chat_id_list)


def work_sheets(list_sheets, sheet, sheet_operaciones='operaciones', sheet_posiciones='posiciones'):
    """
    Trabajo con la base de datos de google sheets
    Al abrir una posicion:
        - escribo la posicion en la hoja de posiciones
        - escribo la operacion en la hoja de operaciones

    Al cerrar una posicion:
        - escribo la operacion en la hoja de operaciones
        - borro la posicion de la hoja de posiciones
    """
    for data in list_sheets:

        if 'open' in data['tipo']:  # Si es una operacion de apertura
            google_sheets.add_operation(sheet, data, sheet_operaciones)
            google_sheets.add_position(sheet, data, sheet_posiciones)

        if 'close' in data['tipo']:  # Si es una operacion de cierre
            google_sheets.add_operation(sheet, data, sheet_operaciones)
            google_sheets.delete_position(sheet, data['ticker'], sheet_posiciones)


def sleep_until_next_minute():
    # Get the current time
    now = datetime.now()

    # Calculate the time for the next minute
    next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)

    # Calculate the number of seconds to sleep
    sleep_seconds = (next_minute - now).total_seconds()
    print(f"Sleeping for {sleep_seconds} seconds")
    # Sleep until the next minute
    time.sleep(sleep_seconds)


if __name__ == '__main__':
    """ PARAMETROS 
    
    Obtendremos los parametros de la hoja de google sheets, y le agregaremos ciertas cosas de los instruments.
    """
    # import config
    # from google_sheets import get_google_sheet, read_all_sheet
    # from api_okx import get_account_md_api, get_account_api, get_data_instruments
    # from keys import API_KEY, API_SECRET, PASSPHRASE
    #
    # # Obtenemos los clients
    # client_md = get_account_md_api()
    # account_api = get_account_api(API_KEY, API_SECRET, PASSPHRASE)
    #
    # # Obtenemos los objetos necesarios
    # gogole_sheet = get_google_sheet(config.FILE_JSON, config.FILE_SHEET)
    #
    # parametros = get_parametros(account_api, gogole_sheet, config.HOJA_PARAMETROS)
    #
    # """ DATA DE PRECIOS """
    #
    # # Descargamos la data de los tickers
    # data = get_data_tickers(parametros, client_md)
    # print(data)
    #
    # # Vemos el ultimo precio de cada ticker
    # last_price = get_last_price(data)
    # print(last_price)

    # # testear el adj_quantity
    # print(adj_quantity(1.6666666666666667, 1))
    # print(adj_quantity(1.6666666666666667, 0.1))
    # print(adj_quantity(1.6666666666666667, 0.01))
    # print(adj_quantity(1.6666666666666667, 0.001))
    #
    # print(adj_quantity(0.9432, 1))
    # print(adj_quantity(0.9432, 0.1))
    # print(adj_quantity(0.9432, 0.01))
    # print(adj_quantity(0.9432, 0.001))
    #
    # print(adj_quantity(1.99999, 1))
    # print(adj_quantity(1.99999, 0.1))
    # print(adj_quantity(1.99999, 0.01))
    # print(adj_quantity(1.99999, 0.001))
    #
    # print(adj_quantity(1.3333, 1))
    # print(adj_quantity(1.3333, 0.1))
    # print(adj_quantity(1.3333, 0.01))
    # print(adj_quantity(1.3333, 0.001))







