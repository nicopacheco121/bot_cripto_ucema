"""
Este será el archivo principal donde estará la estructura del robot

"""

import config
import keys
import google_sheets
import alertas
import time
import api_okx


def run():

    while True:
        now = time.time()

        try:

            # Obtengo los clientes necesarios
            account_api = api_okx.get_account_api(keys.API_KEY, keys.API_SECRET, keys.PASSPHRASE)
            market_data = api_okx.get_market_data()

            # Obtengo las posiciones abiertas



            print(positions)

        except Exception as e:
            print(e)
            # alertas.send_alert('Error en main.py', e)
            time.sleep(10)
            continue

if __name__ == '__main__':
    run()




