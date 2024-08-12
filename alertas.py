import requests
import traceback


def send_telegram_message(bot_token, message, chat_id_list):
    """
    Enviar mensaje a un chat de telegram

    :param bot_token: token del bot de telegram
    :param message: mensaje a enviar
    :param chat_id_list: lista de chat_id a los que se les enviará el mensaje
    """

    message = str(message)  # Convierto el mensaje a string

    for chat_id in chat_id_list:

        chat_id = str(chat_id)  # Convierto el chat_id a string

        try:
            send_text = 'https://api.telegram.org/bot' + bot_token + \
                        '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message
            requests.get(send_text)  # Envío el mensaje

        except:
            traceback.print_exc()
            print("Error al enviar mensaje de telegram")


if __name__ == '__main__':
    """
    La línea if __name__ == '__main__': 
    Se usa para determinar si un script se está ejecutando directamente o siendo importado como módulo. 
    Si el script es el programa principal, el código dentro de este bloque se ejecutará. 
    Esto permite separar la ejecución directa del comportamiento al ser importado.
    """

    """
    - - - - -
    Haciendo un bot de telegram paso a paso.
    
    - Buscar usuario BotFather
    - Escribir /newbot y seguir las instrucciones para crear tu bot. ** Recibirás un token de acceso **
    - Ir al bot generado y darle a /start
    - Obtener tu chatID, para ello abrir una conversacion con @chat_id_echo_bot y escribir /start

    
    El bot generado para la clase es t.me/ucema_alertas_bot.
    - - - - -
    
    """

    # Enviar mensaje a un chat de telegram
    from keys import BOT_TOKEN, CHAT_ID_LIST

    send_telegram_message(BOT_TOKEN,
                          'Long BTC',
                          CHAT_ID_LIST)
