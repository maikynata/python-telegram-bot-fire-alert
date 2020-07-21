import chave
import requests
from telegram.ext import Updater, CommandHandler

def welcome(update, context):
    message = 'Olá '+ update.message.from_user.first_name +'!'
    print(message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def focos(update, context):
    import requests

    baseURL = 'http://queimadas.dgi.inpe.br/queimadas/dados-abertos/api'
    pais_id = int(33)
    estado_id = int(52)
    municipio_id = int(5205307)

    coordenatesURL = baseURL + '/focos/?pais_id={}&estado_id={}&municipio_id={}'.format(pais_id, estado_id, municipio_id)
    countURL = baseURL + '/focos/count?pais_id={}&estado_id={}&municipio_id={}'.format(pais_id, estado_id, municipio_id)

    respCount = requests.get(countURL)
    respCoordenates = requests.get(coordenatesURL)

    if respCoordenates.status_code != 200 or respCount.status_code != 200:
        # This means something went wrong.
        raise requests.exceptions.RequestException('GET /focos/ {}'.format(respCoordenates.status_code))
        raise requests.exceptions.RequestException('GET /focos/count/ {}'.format(respCount.status_code))
    else:

    count = respCount.json()
    if 'Brasil' in count:
        message = 'Número de supostos focos: {}'.format(count['Brasil'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        for todo_item in respCoordenates.json():
            message = 'municipio = {}, localizacao = {}, {}'.format(todo_item['properties']['municipio'],
                                                                todo_item['properties']['latitude'],
                                                                todo_item['properties']['longitude'])
            print(message)
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    else:
        message = "Não há focos registrados por satélite"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    print(message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    token = chave.token
    updater = Updater(token=token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('iniciar', welcome))
    updater.dispatcher.add_handler(CommandHandler('focos', focos))

    updater.start_polling()
    print(str(updater))
    updater.idle()

if __name__ == "__main__":
    main()
