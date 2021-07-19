import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from decimal import Decimal
import csv

def contaFoco(cidade, count):
    count += '&municipio_id={}'.format(cidade)
    respCount = requests.get(count)
    if respCount.status_code != 200:
        raise requests.exceptions.RequestException('GET /focos/count/ {}'.format(respCount.status_code))
    else:
        count = respCount.json()

    if 'Brasil' in count:
        focos = count['Brasil']
    else:
        focos = 0
    
    return focos 

def localFoco(cidade, coord):
    coord += '&municipio_id={}'.format(cidade)
    respCoordinates = requests.get(coord)
    if respCoordinates.status_code != 200:
        raise requests.exceptions.RequestException('GET /focos/ {}'.format(respCoordinates.status_code))
    else:
        message = str() 
        for todo_item in respCoordinates.json():
            message += '{}\nCoordenadas = {}, {}\n'.format(todo_item['properties']['municipio'],
                                                           todo_item['properties']['latitude'],
                                                           todo_item['properties']['longitude'])

            message += 'https://www.google.com.br/maps/place/'
            if todo_item['properties']['latitude'] < 0:
                message += transformaDecimalGrau(todo_item['properties']['latitude']) + 'S'
            else:
                message += transformaDecimalGrau(todo_item['properties']['latitude']) + 'N'

            if todo_item['properties']['longitude'] < 0:
                message += transformaDecimalGrau(todo_item['properties']['longitude']) + 'W'
            else:
                message += transformaDecimalGrau(todo_item['properties']['longitude']) + 'O'
            
            message += '\n\n'
    return message    

def linkAllFocos(cidade, coord):
    coord += '&municipio_id={}'.format(cidade)
    respCoordinates = requests.get(coord)
    if respCoordinates.status_code != 200:
        raise requests.exceptions.RequestException('GET /focos/ {}'.format(respCoordinates.status_code))
    else:
        location = str() 
        for todo_item in respCoordinates.json():
            # location = (todo_item['properties']['latitude'],todo_item['properties']['longitude'])
            location += '{}\nCoordenadas = {}, {}\n'.format(todo_item['properties']['municipio'])

            
            location += 'https://www.google.com/maps/dir//'
            
            
            location += '\n\n TesteLinkAll'
    return location    


def transformaDecimalGrau(grau):
    grauDecimal = int(grau) - Decimal(grau)

    minutosDecimal = Decimal(grauDecimal) * 60
    minutos = int(minutosDecimal)

    segundosDecimal = Decimal(minutosDecimal) - minutos
    segundos = segundosDecimal * 60

    milesimosSeg = segundos - int(segundos)
    milesimos = milesimosSeg * 10
    
    
    coordenada = str(int(abs(grau))) + '°' + str(minutos) + '\u0027' + str(int(segundos)) + '.' + str(int(milesimos)) + "''" 
    return coordenada 


def welcome(update, context):
    message = 'Olá '+ update.message.from_user.first_name +'!'
    print(message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def kalungas(update, context):
    import requests

    baseURL = 'http://queimadas.dgi.inpe.br/queimadas/dados-abertos/api'
    pais_id = int(33)
    estado_id = int(52)
    municipios = [5205307, 5221080, 5213509]

    coordinatesURL = baseURL + '/focos/?pais_id={}&estado_id={}'.format(pais_id, estado_id)
    countURL = baseURL + '/focos/count?pais_id={}&estado_id={}'.format(pais_id, estado_id)

    focos = 0
    for id in municipios:
        focos += contaFoco(id, countURL)
        
    if focos > 0:
        message = 'O número de supostos focos de incêndio na região dos Kalungas é de {}\n'.format(focos)
        for id in municipios:
            message += localFoco(id, coordinatesURL)
            message_linkall = 'Acesse para ver todos os pontos no mapa: https://bot-alerta-fogo.herokuapp.com/'
    else:
        message = 'Não há focos de incêndio registrados na região dos Kalungas'
        # message_linkall = linkAllFocos(id, coordinatesURL)
        message_linkall = 'Acesse para ver todos os pontos no mapa: https://bot-alerta-fogo.herokuapp.com/'

    print(message)
    #print(message_linkall)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message_linkall)

def read_csv(cidade,estado):

    muni = cidade
    uf = estado

    with open('municipio.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            line_count = 0
            if row[0] == muni and row[1] == uf:
                # print(f'O código do municipio é: {row[2]}.')
                cod_muni=row[2]
                return cod_muni
            line_count += 1


def cidade(update, context):
    import requests


    askcidade = 'Olá, digite o nome do município que você deseja ver a localização dos focos de incêndio, Exemplo: Cavalvante.\n\n'
    context.bot.send_message(chat_id=update.effective_chat.id, text=askcidade)
    cidade = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text='Você digitou' + cidade)

    estado(update,context,cidade)

def estado(update, context, city):
    import requests

    askestado = 'Agora digite o nome por extenso, do estado deste município. Exemplo: Goiás.'
    context.bot.send_message(chat_id=update.effective_chat.id, text=askestado)
    estado = update.message.text

    # 'Ou, acesse o menu com o comando /kalungas para ver os focos da região Kalunga. \n\n'
    # context.bot.send_message(chat_id=update.effective_chat.id, text='Você digitou' + cidade)
    
    cidade_resp = city
    cod_muni = read_csv(cidade_resp,estado)

    baseURL = 'http://queimadas.dgi.inpe.br/queimadas/dados-abertos/api'
    pais_id = int(33)
    estado_id = int(52)
    municipios = int(cod_muni)

    coordinatesURL = baseURL + '/focos/?pais_id={}&estado_id={}'.format(pais_id, estado_id)
    countURL = baseURL + '/focos/count?pais_id={}&estado_id={}'.format(pais_id, estado_id)

    focos = 0
    focos += contaFoco(cidade_resp, countURL)
        
    if focos > 0:
        message = 'O número de supostos focos de incêndio na região deste Município código: '+ cidade +' é de {}\n\n'.format(focos)
        message += localFoco(cidade_resp, coordinatesURL)
        message_linkall = 'Acesse para ver todos os pontos no mapa: https://bot-alerta-fogo.herokuapp.com/'
    else:
        message = 'Não há focos de incêndio registrados na região deste Município'

    print(message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message_linkall)


def ajuda(update, context):
    message = 'Os dados apresentados pelo Labareda Alerta são atualizados a cada 3 horas, nos seguintes horários: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 (UTC) Conforme o site http://queimadas.dgi.inpe.br.'
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    token = os.environ['TOKEN']
    updater = Updater(token=token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('iniciar', welcome))
    updater.dispatcher.add_handler(CommandHandler('kalungas', kalungas))
    updater.dispatcher.add_handler(CommandHandler('cidade', cidade))
    updater.dispatcher.add_handler(CommandHandler('ajuda', ajuda))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, cidade))

    updater.start_polling()
    print(str(updater))
    updater.idle()

if __name__ == "__main__":
    main()
