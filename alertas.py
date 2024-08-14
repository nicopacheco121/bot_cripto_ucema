import requests


def send_telegram_message(bot_token, message, chat_id_list):
    """
    Envía un mensaje a uno o varios chats de Telegram.

    :param bot_token: Token del bot de Telegram (string)
    :param message: Mensaje a enviar
    :param chat_id_list: Lista de chat_ids a los que se enviará el mensaje
    """

    message = str(message)  # Convierto el mensaje a string

    for chat_id in chat_id_list:

        chat_id = str(chat_id)  # Convierto el chat_id a string

        try:
            # Construimos la URL para la API de Telegram usando f-strings
            send_text = 'https://api.telegram.org/bot' + bot_token + \
                        '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message

            response = requests.get(send_text)  # Enviamos la solicitud GET a la API de Telegram

            response.raise_for_status()  # Verificamos si la solicitud fue exitosa

        except requests.RequestException as e:
            print(f"Error al enviar mensaje de Telegram al chat_id {chat_id}: {e}")


if __name__ == '__main__':
    """
    Sobre if __name__ == '__main__': 
    Este bloque se ejecuta solo si el script se ejecuta directamente (no si se importa como módulo).
    Es útil para pruebas o para ejecutar el script como un programa independiente.
    """

    # Instrucciones para crear y configurar un bot de Telegram
    """
    Pasos para crear un bot de Telegram:
        1. Busca el usuario @BotFather en Telegram.
        2. Inicia una conversación y escribe /newbot
        3. Sigue las instrucciones para crear tu bot:
         - Elige un nombre para tu bot
         - Elige un nombre de usuario para tu bot (debe terminar en 'bot')
        4. BotFather te dará un ** token de acceso **. Guárdalo de forma segura.
        5. Inicia una conversación con tu nuevo bot y envía el comando /start
        
    Para obtener tu chat_id:
        1. Busca el bot @userinfobot en Telegram
        2. Inicia una conversación y envía cualquier mensaje
        3. El bot te responderá con tu información, incluyendo tu chat_id
        
        El bot creado para esta clase es: t.me/ucema_alertas_bot
    """

    # Ejemplo de cómo usar la función
    from keys import BOT_TOKEN, CHAT_ID_LIST

    send_telegram_message(BOT_TOKEN, 'Long BTC', CHAT_ID_LIST)
