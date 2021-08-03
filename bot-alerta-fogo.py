import os
import requests
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from decimal import Decimal
import csv

STATE1 = 1
STATE2 = 2
STATE3 = 3

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
        messageList = [] 
        for todo_item in respCoordinates.json():
            message = '{}\nCoordenadas = {}, {}\nSatélite:{}\n'.format(todo_item['properties']['municipio'],
                                                           todo_item['properties']['latitude'],
                                                           todo_item['properties']['longitude'],
                                                           todo_item['properties']['satelite'])

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

            messageList.append(message)

    return messageList    

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


# def welcome(update, context):
#     try:
#         firstName = update.message.from_user.first_name
#         message = 'Olá, ' + firstName + '!'
#         context.bot.send_message(chat_id=update.effective_chat.id, text=message)
#     except Exception as e:
#         print(str(e))


def welcome(update, context):
    # message = 'Olá '+ update.message.from_user.first_name +'!'
    # print(message)
    # context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    try:
        firstName = update.message.from_user.first_name
        message = 'Olá, ' + firstName + '!'
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        message = 'Digite o nome do município que você deseja ver a localização dos focos de incêndio, Exemplo: Cavalcante.\n\n'
        update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([], one_time_keyboard=True))
        return STATE1
    except Exception as e:
        print(str(e))

    # cidade = update.message.text

    # context.bot.send_message(chat_id=update.effective_chat.id, text='Você digitou' + cidade)

    # estado(update,context,cidade)


def kalungas(update, context):
    
    firstName = update.message.from_user.first_name
    message = 'Olá, ' + firstName + '! Aguarde um instante, estou verificando se existem focos de incêndio na região dos Kalungas...'
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

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
            # message_linkall = 'Acesse para ver todos os pontos no mapa: https://bot-alerta-fogo.herokuapp.com/'
    else:
        message = 'Pronto, não há focos de incêndio registrados na região dos Kalungas nas últimas horas de hoje. Consulte novamente mais tarde'
        # message_linkall = linkAllFocos(id, coordinatesURL)
        # message_linkall = 'Acesse para ver todos os pontos no mapa: https://bot-alerta-fogo.herokuapp.com/'

    # print(message)
    # print(message_linkall)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    # context.bot.send_message(chat_id=update.effective_chat.id, text=message_linkall)
    return ConversationHandler.END

def read_csv_cidade(cidade,estado):

    muni = cidade
    uf = estado

    with open('municipio.csv', encoding="latin1") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            line_count = 0
            if row[0] == muni and row[1] == uf:
                # print(f'O código do municipio é: {row[2]}.')
                cod_muni = row[2]
                return cod_muni
            line_count += 1

def read_csv_estado(estado):

    uf = estado

    with open('estados.csv', encoding="latin1") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            line_count = 0
            if row[0] == uf:
                # print(f'O código do municipio é: {row[2]}.')
                estado_nome = row[1]
                return estado_nome
            line_count += 1


def estado(update, context):

    context.user_data["city"] = update.message.text
    cidade_resp = context.user_data["city"]
    print(cidade_resp)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Você respondeu a cidade: ' + cidade_resp)
    
    if len(cidade_resp) < 3:
        message = """O nome da cidade está muito curto... 
                        \nInforma mais pra gente, por favor?"""
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return STATE1
    else:
        message = "Muito obrigado!"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        
    try:

        message = "Agora escolha o Estado deste Município.\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        regiao_centro = 'Região Centro-Oeste:'
        keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("GO", callback_data='52'),
                InlineKeyboardButton("MT", callback_data='51'),
                InlineKeyboardButton("MS", callback_data='50'),
                InlineKeyboardButton("DF", callback_data='53'),]])
        update.message.reply_text(regiao_centro, reply_markup=keyboard)

        regiao_norte = 'Região Norte:'
        keyboard2 = InlineKeyboardMarkup(
                [[InlineKeyboardButton("AM", callback_data='13'),
                InlineKeyboardButton("AC", callback_data='12'),
                InlineKeyboardButton("AP", callback_data='16'),
                InlineKeyboardButton("RR", callback_data='14'),
                InlineKeyboardButton("PA", callback_data='15'),
                InlineKeyboardButton("TO", callback_data='17'),
                InlineKeyboardButton("RO", callback_data='11'),]])
        update.message.reply_text(regiao_norte, reply_markup=keyboard2)

        regiao_nordeste = 'Região Nordeste:'
        keyboard3 = InlineKeyboardMarkup(
                [[InlineKeyboardButton("MA", callback_data='21'),
                InlineKeyboardButton("PI", callback_data='22'),
                InlineKeyboardButton("CE", callback_data='23'),
                InlineKeyboardButton("PB", callback_data='25'),
                InlineKeyboardButton("PE", callback_data='26'),],
                    [InlineKeyboardButton("AL", callback_data='27'),
                    InlineKeyboardButton("SE", callback_data='28'),
                    InlineKeyboardButton("BA", callback_data='29'),
                    InlineKeyboardButton("RN", callback_data='24')]])
        update.message.reply_text(regiao_nordeste, reply_markup=keyboard3)
        
        # regiao_nordeste_2 = '+'
        # keyboard3_1 = InlineKeyboardMarkup(
        #         [[InlineKeyboardButton("RN", callback_data='24'),]])
        # update.message.reply_text(regiao_nordeste_2, reply_markup=keyboard3_1)

        regiao_sudeste = 'Região Suteste:'
        keyboard4 = InlineKeyboardMarkup(
                [[InlineKeyboardButton("SP", callback_data='35'),
                InlineKeyboardButton("ES", callback_data='32'),
                InlineKeyboardButton("RJ", callback_data='33'),
                InlineKeyboardButton("MG", callback_data='31'),]])
        update.message.reply_text(regiao_sudeste, reply_markup=keyboard4)

        regiao_sul= 'Região Sul:'
        keyboard5 = InlineKeyboardMarkup(
                [[InlineKeyboardButton("PR", callback_data='41'),
                InlineKeyboardButton("SC", callback_data='42'),
                InlineKeyboardButton("RS", callback_data='43'),]])
        update.message.reply_text(regiao_sul, reply_markup=keyboard5)
        
    except Exception as e:
            print(str(e))
        
    return STATE2


def result_focos(update, context):

    try:
        cidade_resp = context.user_data["city"]
        print("Cidade do context.user_data: " + cidade_resp)

        try:
            query = update.callback_query
            print(str(query.data))
            # message = 'Você escolheu o Estado: ' + str(query.data) 
            # context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        except Exception as e: 
            print(str(e))
            return ConversationHandler.END
        
        cod_estado = str(query.data)
        estado_nome = read_csv_estado(cod_estado)

        print("Estado selecionado no menu query.data: " + cod_estado)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Você escolheu no menu o Estado: ' + estado_nome)
        
        cod_muni = read_csv_cidade(cidade_resp,estado_nome)
        
        context.bot.send_message(chat_id=update.effective_chat.id, text='O código do IBGE deste município é: ' + cod_muni)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Muito obrigado! Já estou verificando se existem focos de incêndio na região de ' + cidade_resp + '...')

        baseURL = 'http://queimadas.dgi.inpe.br/queimadas/dados-abertos/api'
        pais_id = int(33)
        estado_id = int(cod_estado)
        municipio = int(cod_muni)

        coordinatesURL = baseURL + '/focos/?pais_id={}&estado_id={}'.format(pais_id, estado_id)
        countURL = baseURL + '/focos/count?pais_id={}&estado_id={}'.format(pais_id, estado_id)

        focos = 0
        focos += contaFoco(cod_muni, countURL)
            
        if focos > 0:
            messageCount = 'O número de supostos focos de incêndio na região deste Município código: '+ cod_muni +' é de {}\n\n'.format(focos)
            context.bot.send_message(chat_id=update.effective_chat.id, text=messageCount)
            messageList = localFoco(cod_muni, coordinatesURL)
            
            for foco in messageList:
                messageFocoItem = foco
                context.bot.send_message(chat_id=update.effective_chat.id, text=messageFocoItem)
                print(messageFocoItem)

            endmessage = 'Consulta finalizada, utilize o menu para fazer uma nova consulta.'
            context.bot.send_message(chat_id=update.effective_chat.id, text=endmessage)
            
        else:
            message = 'Não há focos de incêndio registrados na região deste Município.'
            print(message)

            endmessage = 'Consulta finalizada, utilize o menu para fazer uma nova consulta.'
            context.bot.send_message(chat_id=update.effective_chat.id, text=endmessage)
        
        return ConversationHandler.END

    except Exception as e: 
        print(str(e))
        message = """O nome do município não foi encontrado, por favor, verifique se o mesmo está escrito corretamente, exemplo:
        - Cavalcante
        - Uruçuí
        - Palmeiras de Goiás
    Favor não escrever em letras maiúsculas. Favor verificar se a cidade pertence ao Estado selecionado.
    Utilize o menu /iniciar para consultar novamente. Obrigado!"""
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return ConversationHandler.END


def ajuda(update, context):
    message = """Os dados apresentados pelo Labareda Alerta são atualizados a cada 3 horas, nos seguintes horários:
    00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 (UTC). Saiba mais no site http://queimadas.dgi.inpe.br.\n\n
    - Utilize o menu para fazer as consultas:\n
    /iniciar - Para consultar focos de qualquer cidade do Brasil
    /kalungas - Para consultar os focos da região Kalunga"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return ConversationHandler.END


def cancel(update, context):
    return ConversationHandler.END

def main():
    token = os.environ['TOKEN']
    updater = Updater(token=token, use_context=True)

    # updater.dispatcher.add_handler(CommandHandler('iniciar', welcome))
    updater.dispatcher.add_handler(CommandHandler('kalungas', kalungas))
    # updater.dispatcher.add_handler(CommandHandler('cidade', cidade))
    updater.dispatcher.add_handler(CommandHandler('ajuda', ajuda))
    # updater.dispatcher.add_handler(MessageHandler(Filters.text, cidade))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('iniciar', welcome)],
        states={
            STATE1: [MessageHandler(Filters.text, estado)],
            STATE2: [MessageHandler(Filters.text, result_focos)],
            STATE3: [MessageHandler(Filters.text, ajuda)],
        },
        fallbacks=[CommandHandler('cancel', cancel)])
    updater.dispatcher.add_handler(conversation_handler)

    updater.dispatcher.add_handler(CallbackQueryHandler(result_focos))


    updater.start_polling()
    print(str(updater))
    updater.idle()

if __name__ == "__main__":
    main()
