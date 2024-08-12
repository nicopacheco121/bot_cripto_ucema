import gspread
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
    - operaciones
    
    """

    import config

    # Obtenemos los objetos necesarios
    gogole_sheet = get_google_sheet(config.FILE_JSON, config.FILE_SHEET)

    sheet_parametros = get_sheet(gogole_sheet, config.HOJA_PARAMETROS)

    # Leemos los datos de la hoja parametros
    print(sheet_parametros.get_all_records())

    # Escribimos en la hoja de testeo
    sheet_testeo = get_sheet(gogole_sheet, config.HOJA_TESTEO)
    sheet_testeo.update(values=[['Testeo']], range_name='A1')

    # otra forma
    sheet_testeo.update_cell(row=2, col=1, value='Testeo')


