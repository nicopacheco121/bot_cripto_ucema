import gspread
from google.auth.exceptions import GoogleAuthError
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound
import pprint
from typing import List, Dict, Any


def get_google_sheet(file_json: str, g_sheet: str) -> gspread.Spreadsheet:
    """
    Obtiene el objeto Google Sheet para acceder a las hojas de cálculo.

    :param file_json: Ruta al archivo JSON con las credenciales de Google Sheets
    :param g_sheet: Nombre del Google Sheet
    :return: Objeto Spreadsheet de gspread
    :raises GoogleAuthError: Si hay un problema con la autenticación
    :raises SpreadsheetNotFound: Si no se encuentra el Google Sheet especificado
    """

    try:
        gc = gspread.service_account(filename=file_json)
        sh = gc.open(g_sheet)
        return sh
    except GoogleAuthError as e:
        print(f"Error de autenticación: {e}")
        raise
    except SpreadsheetNotFound:
        print(f"No se encontró el Google Sheet '{g_sheet}'")
        raise


def get_sheet(sh: gspread.Spreadsheet, sheet_name: str) -> gspread.Worksheet:
    """
    Obtiene una hoja de cálculo específica del Google Sheet.

    :param sh: Objeto Spreadsheet de gspread
    :param sheet_name: Nombre de la hoja de cálculo
    :return: Objeto Worksheet de gspread
    :raises WorksheetNotFound: Si no se encuentra la hoja especificada
    """
    try:
        return sh.worksheet(sheet_name)
    except WorksheetNotFound:
        print(f"No se encontró la hoja '{sheet_name}'")
        raise


def read_all_sheet(gs: gspread.Spreadsheet, sheet_name: str) -> List[Dict[str, Any]]:
    """
    Lee todos los datos de una hoja y los devuelve como una lista de diccionarios.

    :param gs: Objeto Spreadsheet de gspread
    :param sheet_name: Nombre de la hoja de cálculo
    :return: Lista de diccionarios con los datos de la hoja
    """
    sheet = get_sheet(gs, sheet_name)
    return sheet.get_all_records()


def add_position(gs: gspread.Spreadsheet, data: Dict[str, Any], sheet_name: str = 'posiciones') -> None:
    """
    Agrega una nueva posición a la hoja de posiciones.

    :param gs: Objeto Spreadsheet de gspread
    :param data: Diccionario con los datos de la posición
    :param sheet_name: Nombre de la hoja de posiciones (por defecto 'posiciones')
    """

    # reorganizo los datos para que coincidan con las columnas
    columns = ['ticker', 'execution_time', 'side', 'margen', 'leverage', 'nocional', 'avg_price', 'contratos',
               'stop_loss', 'take_profit', 'fee']

    # genero una lista en base al orden de las columnas
    data = [data[col] for col in columns]

    sheet = get_sheet(gs, sheet_name)  # obtengo la hoja de posiciones
    sheet.append_row(data)  # agrego la fila a continuación de la última fila con datos


def add_operation(gs: gspread.Spreadsheet, data: Dict[str, Any], sheet_name: str = 'operaciones') -> None:
    """
    Agrega una nueva operación a la hoja de operaciones.

    :param gs: Objeto Spreadsheet de gspread
    :param data: Diccionario con los datos de la operación
    :param sheet_name: Nombre de la hoja de operaciones (por defecto 'operaciones')
    """

    # reorganizo los datos para que coincidan con las columnas
    columns = ['ticker', 'tipo', 'execution_time', 'side', 'margen', 'leverage', 'nocional', 'avg_price', 'contratos',
               'fee', 'motivo']

    # si es de cierre, sumo el pnl
    if data.get('tipo') == 'close':
        columns.append('pnl')

    # genero una lista en base al orden de las columnas
    data = [data[col] for col in columns]

    sheet = get_sheet(gs, sheet_name)  # obtengo la hoja de operaciones
    sheet.append_row(data)  # agrego la fila a continuación de la última fila con datos


def delete_position(gs: gspread.Spreadsheet, ticker: str, sheet_name: str = 'posiciones') -> None:
    """
    Borra una posición de la hoja de posiciones.

    :param gs: Objeto Spreadsheet de gspread
    :param ticker: Ticker de la posición a borrar
    :param sheet_name: Nombre de la hoja de posiciones (por defecto 'posiciones')
    """

    sheet = get_sheet(gs, sheet_name)
    data = sheet.get_all_records()  # obtengo una lista de diccionarios con los datos de la hoja

    # Buscamos la posicion
    for i, d in enumerate(data):  # enumerate me da el indice y el valor de la lista
        if d['ticker'] == ticker:
            # Borramos la fila
            sheet.delete_rows(i + 2)  # +2 porque las filas en sheets empiezan en 1 y hay una fila de encabezado

            return

    print(f"No se encontró ninguna posición con el ticker '{ticker}'.")  # si no se encontró la posición


if __name__ == '__main__':
    """
    Instrucciones para configurar Google Sheets:
    
    1. Generar un proyecto en la consola de Google Cloud: https://console.cloud.google.com/
    2. Habilitar la API de Google Sheets para el proyecto.
    3. Crear una cuenta de servicio y descargar el archivo JSON de credenciales.
    4. Compartir el Google Sheet con el correo de la cuenta de servicio.

    Para el proceso completo y mejor explicado, consultar este hilo de twitter que hice hace un tiempo:
    https://x.com/nicopachecolas/status/1633568913844781058
    
    Con dicho proceso obtienen un json y un correo para compartir el sheet a utilizar.
    
    En este caso el sheet que vamos a utilizar es "ucema_bot", link:
    https://docs.google.com/spreadsheets/d/1YotU4XUKp4AslkM3gdeEtH_u3kJHWBGuhMWuPyUoBy8/edit?usp=sharing
    
    Hojas utilizadas:
    - parametros
    - posiciones
    - operaciones
    
    """

    import config

    try:
        gogole_sheet = get_google_sheet(config.FILE_JSON, config.FILE_SHEET)  # Obtener el objeto Google Sheet

        """ PARAMETROS """
        # Leer y mostrar los parámetros
        sheet_parametros = get_sheet(gogole_sheet, config.HOJA_PARAMETROS)
        pprint.pprint(sheet_parametros.get_all_records())

        # O tambien lo hacemos con la funcion que hicimos para ello
        sheet_parametros = read_all_sheet(gogole_sheet, config.HOJA_PARAMETROS)
        pprint.pprint(sheet_parametros)

        """ POSICIONES
        Vamos a seguir la estructura de columnas ya que esta hoja no solo leeremos sino tambien que escribiremos"""
        # Ejemplo: Agregar una nueva posición
        data = {
            'avg_price': 60000,
            'contratos': 2,
            'execution_time': '2024-08-20 10:00:00',
            'fee': -0.05,
            'leverage': 5,
            'margen': 100,
            'nocional': 500,
            'side': 'long',
            'stop_loss': 59800,
            'take_profit': 61000,
            'ticker': 'BTC-USDT-SWAP'
        }
        add_position(gogole_sheet, data, config.HOJA_POSICIONES)

        # Escribimos otra posicion ejemplo de ETH
        data = {
            'avg_price': 3000,
            'contratos': 2,
            'execution_time': '2024-08-20 10:00:00',
            'fee': -0.05,
            'leverage': 5,
            'margen': 100,
            'nocional': 500,
            'side': 'long',
            'stop_loss': 2900,
            'take_profit': 3300,
            'ticker': 'ETH-USDT-SWAP'
        }
        add_position(gogole_sheet, data, config.HOJA_POSICIONES)

        # # Escribimos en la hoja de testeo
        # sheet_testeo = get_sheet(gogole_sheet, config.HOJA_TESTEO)
        # sheet_testeo.update(values=[['Testeo']], range_name='A1')
        # # otra forma
        # sheet_testeo.update_cell(row=2, col=1, value='Testeo')

        # Borramos la posicion de BTC
        delete_position(gogole_sheet, 'BTC-USDT-SWAP', config.HOJA_POSICIONES)

        """ OPERACIONES 
        Si es de cierre, se suma el pnl        
        """

        open_operation = {
            'avg_price': 60000,
            'contratos': 2,
            'execution_time': '2024-08-20 10:00:00',
            'fee': -0.05,
            'leverage': 5,
            'margen': 100,
            'nocional': 500,
            'motivo': 'rsi',
            'side': 'long',
            'ticker': 'BTC-USDT-SWAP',
            'tipo': 'open'}
        add_operation(gogole_sheet, open_operation, config.HOJA_OPERACIONES)

        close_operation = {
            'avg_price': 60000,
            'contratos': 2,
            'execution_time': '2024-08-20 10:00:00',
            'fee': -0.05,
            'leverage': 5,
            'margen': 100,
            'nocional': 500,
            'motivo': 'stop_loss',
            'pnl': 'pnl',
            'side': 'long',
            'ticker': 'BTC-USDT-SWAP',
            'tipo': 'close'}
        add_operation(gogole_sheet, close_operation, config.HOJA_OPERACIONES)

    except Exception as e:
        print(f"Se produjo un error: {e}")
