import gspread
import pprint
import time


def get_google_sheet(file_json, g_sheet):
    """
    Obtengo el google sheet con el que luego podre acceder a las hojas de calculo y leerlas o escribir en ellas.

    :param file_json: credenciales de google sheets
    :param g_sheet: nombre del google sheet
    """

    gc = gspread.service_account(filename=file_json)
    sh = gc.open(g_sheet)

    return sh


def get_sheet(sh, sheet_name):
    """
    Obtengo la hoja de calculo del google sheet

    :param sh: google sheet
    :param sheet_name: nombre de la hoja de calculo
    """

    sheet = sh.worksheet(sheet_name)

    return sheet


def read_all_sheet(gs, sheet_name):
    """
    Leo la hoja y entrego un diccionario con los datos
    ticker : {parametros}

    :param gs: objeto de google sheets
    :param sheet_name:
    :return:
    """

    sheet = get_sheet(gs, sheet_name)
    data = sheet.get_all_records()

    return data


def add_position(gs, data, sheet_name='posiciones'):
    """
    Agrego una nueva posicion a la hoja de posiciones

    columnas = [ticker	execution_time	side	margen	leverage	nocional	avx_price	quantity	contratos	stop_loss	take_profit	fee]

    :param gs: objeto de google sheets
    :param sheet_name: nombre de la hoja de posiciones
    :param data: lista con los datos de la posicion
    """

    sheet = get_sheet(gs, sheet_name)
    sheet.append_row(data)


def add_operation(gs, data, sheet_name='operaciones'):
    """
    Agrego una nueva operacion a la hoja de operaciones

    columnas [ticker	tipo	execution_time	side	margen	leverage	nocional	avx_price	quantity	contratos	fee	motivo]

    :param gs: objeto de google sheets
    :param sheet_name: nombre de la hoja de operaciones
    :param data: lista con los datos de la operacion
    """

    sheet = get_sheet(gs, sheet_name)
    sheet.append_row(data)


def detele_position(gs, ticker, sheet_name='posiciones'):
    """
    Borro una posicion de la hoja de posiciones

    :param gs: objeto de google sheets
    :param sheet_name: nombre de la hoja de posiciones
    :param ticker: ticker de la posicion a borrar
    """

    sheet = get_sheet(gs, sheet_name)
    data = sheet.get_all_records()

    # Buscamos la posicion de BTC
    for i, d in enumerate(data):
        if d['ticker'] == ticker:

            # Borramos la fila
            sheet.delete_rows(i + 2)
            # IMPORTANTE, vemos que en sheets las filas no arranca de 0, arranca de 1
            break


if __name__ == '__main__':

    """
    Para configurar el sheets se debe generar un proyecto en la consola de google.
    El proceso entero lo tienen en el siguiente hilo de twitter:
    
    https://x.com/nicopachecolas/status/1633568913844781058
    
    Con dicho proceso obtienen un json y un correo para compartir el sheet a utilizar.
    
    En este caso el sheet que vamos a utilizar es "ucema_bot", link:
    https://docs.google.com/spreadsheets/d/1YotU4XUKp4AslkM3gdeEtH_u3kJHWBGuhMWuPyUoBy8/edit?usp=sharing
    
    Las hojas que utilizaremos son:
    - parametros
    - posiciones
    - operaciones
    
    """

    import config

    # Obtenemos los objetos necesarios
    gogole_sheet = get_google_sheet(config.FILE_JSON, config.FILE_SHEET)

    """ PARAMETROS """
    # Leemos los datos de la hoja parametros
    sheet_parametros = get_sheet(gogole_sheet, config.HOJA_PARAMETROS)
    pprint.pprint(sheet_parametros.get_all_records())

    # O tambien lo hacemos con la funcion que hicimos para ello
    pprint.pprint(read_all_sheet(gogole_sheet, config.HOJA_PARAMETROS))


    """ POSICIONES
    Vamos a seguir la estructura de columnas ya que esta hoja no solo leeremos sino tambien que escribiremos

    columnas = [ticker	execution_time	side	margen	leverage	nocional	avx_price	quantity	contratos	stop_loss	take_profit	fee]

    """
    # Escribimos una nueva posicion ejemplo
    data = ['BTC-USDT-SWAP', '2024-08-20 10:00:00', 'long', 100, 5, 500, 60000, 0.002, 2, 59800, 61000, -0.05]
    add_position(gogole_sheet, data, config.HOJA_POSICIONES)

    # Escribimos otra posicion ejemplo de ETH
    data = ['BNB-USDT-SWAP', '2024-08-20 10:00:00', 'long', 100, 5, 500, 3000, 0.002, 2, 2900, 3300, -0.05]
    add_position(gogole_sheet, data, config.HOJA_POSICIONES)

    # Borramos la posicion de BTC
    detele_position(gogole_sheet, 'BTC-USDT-SWAP', config.HOJA_POSICIONES)

    # # Escribimos en la hoja de testeo
    # sheet_testeo = get_sheet(gogole_sheet, config.HOJA_TESTEO)
    # sheet_testeo.update(values=[['Testeo']], range_name='A1')
    #
    # # otra forma
    # sheet_testeo.update_cell(row=2, col=1, value='Testeo')

    """ OPERACIONES 
    
    columnas [ticker	tipo	execution_time	side	margen	leverage	nocional	avx_price	quantity	contratos	fee	motivo]
    
    """

    open_operation = ['BTC-USDT-SWAP', 'open', '2024-08-20 10:00:00', 'long', 100, 5, 500, 60000, 0.002, 2, -0.05]
    add_operation(gogole_sheet, open_operation, config.HOJA_OPERACIONES)

    close_operation = ['BTC-USDT-SWAP', 'close', '2024-08-20 10:00:00', 'long', 100, 5, 500, 60000, 0.002, 2, -0.05, 'stop_loss']
    add_operation(gogole_sheet, close_operation, config.HOJA_OPERACIONES)
