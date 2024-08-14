import ta.trend
import ta.momentum


def get_adx(df):
    data = df.copy()  # hacemos una copia para no modificar el original y evitar warnings

    # Initialize the ADX indicator
    adx_indicator = ta.trend.ADXIndicator(high=data['high'],
                                          low=data['low'],
                                          close=data['close'],
                                          window=14,
                                          fillna=False)

    # Calculate the ADX
    data['ADX'] = adx_indicator.adx()

    return data['ADX']


def get_rsi(df):
    data = df.copy()

    # Initialize the RSI indicator
    rsi_indicator = ta.momentum.RSIIndicator(close=data['close'], window=14, fillna=False)

    # Calculate the RSI
    data['RSI'] = rsi_indicator.rsi()

    return data['RSI']


def cruce_ema(df, slow, fast):
    """
    Cruce de medias exponenciales
    :param df:
    :param slow:
    :param fast:
    :return:
    """
    data = df.copy()

    data['ema_fast'] = ta.trend.EMAIndicator(close=data['close'], window=fast, fillna=False).ema_indicator()
    data['ema_slow'] = ta.trend.EMAIndicator(close=data['close'], window=slow, fillna=False).ema_indicator()

    data['cruce'] = data['ema_fast'] / data['ema_slow'] -1

    return data['cruce']


def add_indicadores(df, parametros):
    """
    Agrega los indicadores al df
    :param df:
    :return:
    """

    data = df.copy()
    slow = parametros['ema_slow']
    fast = parametros['ema_fast']

    data['ADX'] = get_adx(data)
    data['RSI'] = get_rsi(data)
    data['cruce'] = cruce_ema(data, slow, fast)

    return data


if __name__ == '__main__':
    """
    Obtenemos el precio, como vimos en functions
    """
    import config
    from google_sheets import get_google_sheet, read_all_sheet
    from api_okx import get_account_md_api, get_account_api
    from functions import get_data_tickers, get_parametros
    from keys import API_KEY, API_SECRET, PASSPHRASE

    # Obtenemos el client_md
    client_md = get_account_md_api()
    account_api = get_account_api(API_KEY, API_SECRET, PASSPHRASE)

    # Obtenemos los objetos necesarios
    gogole_sheet = get_google_sheet(config.FILE_JSON, config.FILE_SHEET)
    parametros = get_parametros(account_api, gogole_sheet)

    # Descargamos la data de los tickers
    data = get_data_tickers(parametros, client_md)
    print(data)

    # Agregamos los indicadores
    data_indicadores = {}
    for k, v in data.items():
        data_indicadores[k] = add_indicadores(v, parametros[k])

    print(data_indicadores)

