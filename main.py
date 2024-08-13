"""
Este será el archivo principal donde estará la estructura del robot

"""

import config
from keys import API_KEY, API_SECRET, PASSPHRASE, BOT_TOKEN, CHAT_ID_LIST
import google_sheets
import alertas
import time
import api_okx
import functions
from datetime import datetime
import pprint
import traceback


def run():

    while True:

        print('Iniciando bot')

        try:
            now = datetime.now()
            print(f'Iniciando bot {datetime.now()}')

            # Obtengo los clientes necesarios
            account_api = api_okx.get_account_api(API_KEY, API_SECRET, PASSPHRASE)
            account_trade_api = api_okx.get_account_trade_api(API_KEY, API_SECRET, PASSPHRASE)
            client_md = api_okx.get_account_md_api()
            sheet = google_sheets.get_google_sheet(config.FILE_JSON, config.FILE_SHEET)

            # Voy a generar listas para enviar a telegram y a google sheets. Lo hago de esta manera para hacerlo al
            # final y no tener que hacerlo en cada iteración
            to_telegram = []
            to_sheets = []

            # Base de datos de parametros
            parametros = functions.get_parametros(account_api, sheet, config.HOJA_PARAMETROS)

            print('\nParametros')
            pprint.pprint(parametros)

            # # Base de datos de posiciones abiertas
            # posiciones = google_sheets.read_all_sheet(sheet, config.HOJA_POSICIONES)
            # print('\nPosiciones')
            # pprint.pprint(posiciones)

            posiciones = []

            # Descargo la data de los tickers
            data = functions.get_data_tickers(parametros, client_md)
            print('\nData tickers')
            print(data)

            # Close positions
            # si cierro una posicion no permito que se abra de nuevo en la misma corrida
            posiciones_cerradas = functions.close_positions(posiciones, data, account_trade_api, to_telegram, to_sheets)
            print(f'\nPosiciones cerradas: {posiciones_cerradas}')

            # # Veo balance en USDT luego de cerrar posiciones
            # balance = api_okx.get_usdt_balance(account_api)
            # print(f'\nBalance USDT {balance}')

            balance = 5000

            # Seteo leverage
            print('\nSeteo leverage')
            functions.fx_set_leverage(account_api, parametros)

            # Calculo indicadores
            print('\nCalculo indicadores')
            data = functions.calculate_indicators(data, parametros)

            # Abro posiciones
            print('\nAbro posiciones')
            functions.open_positions(parametros, posiciones, posiciones_cerradas, balance, data, account_trade_api, to_telegram, to_sheets)

            # Envio telegram
            print('\nEnvio telegram')
            functions.send_telegram_messages(to_telegram, BOT_TOKEN, CHAT_ID_LIST)

            # Guardo en google sheets
            print('\nGuardo en google sheets')
            functions.work_sheets(to_sheets, sheet)

            # print duration bot como la diferencia entre now y el inicio
            print(f'Duration bot: {datetime.now() - now}')

            # Duermo hasta el siguiente minuto calendario
            functions.sleep_until_next_minute()

        except Exception as e:
            traceback.print_exc()
            print(e)
            # Envio alerta
            alertas.send_telegram_message(BOT_TOKEN, f'Error en bot: {e}', CHAT_ID_LIST)

            functions.sleep_until_next_minute()
            # Arranco el bot de nuevo
            continue


if __name__ == '__main__':
    run()




