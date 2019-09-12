import logging
import telebot
from telebot import apihelper
import requests
import json
import random
import hh


parameters = json.loads(open('conf.json').read())

TELE_PROXY=parameters['preferences']['tchat_proxy']
TELE_TOKEN=parameters['preferences']['tchat_token']
TELE_PROTOCOL=parameters['preferences']['tchat_protocol']
TELE_CHATID=parameters['preferences']['tchat_id']

hellowarray=['Привет','Алоха','Чего хочешь?']

logger=telebot.logger
telebot.logger.setLevel(logging.DEBUG)
apihelper.proxy = {TELE_PROTOCOL: TELE_PROXY}
bot=telebot.TeleBot(TELE_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, "Привет. Меня зовут @BIBot.\n Я могу дать оценку предложений работодателей в Москве.\n"\
                     "Напиши ключевые слова через запятую, например, 'frontend Разработчик, angular'")
    bot.register_next_step_handler(message, get_vacancyestimate)

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.from_user.id,"Привет. Меня зовут @BIBot.\n Я могу дать оценку предложений работодателей в Москве.\n" \
                         "Напиши ключевые слова через запятую, например, 'frontend Разработчик, angular'")
        bot.register_next_step_handler(message, get_vacancyestimate)
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понял.')

def get_vacancyestimate(message):
    snext = message.text.lower().split(',')
    a = []
    for i in snext:
        if i.startswith(' '):
            i = i[1:]
        a.append("'" + i + "'")
    stro = ' AND '.join(a)

    #bot.send_message(message.chat.id, 'Преобразовал в:' + stro)
    bot.send_message(message.chat.id, 'Опрашиваю HR-ов....')
    df=hh.GetPositionSalaryEstimate(stro, 'RUR')
    bot.send_message(message.chat.id,'Для позиции ' + message.text.lower() + '\nРаботодатели указывают следующие предложения:\n' +
                     'Минимальная - ' + repr(df[0]) + '\nМаксимальная - ' + repr(df[1]) + '\nМедианная - ' + repr(df[2]) + '\nСредняя - ' + repr(df[3]))
    imgwordcloud = open(df[4], 'rb')
    bot.send_photo(message.chat.id,imgwordcloud)

    bot.send_message(message.from_user.id, "Еще будем искать?")
    bot.register_next_step_handler(message, get_vacancy_onecemore)

def get_vacancy_onecemore(message):
    if message.text.lower() == 'да':
        bot.send_message(message.from_user.id, "Какая позиция?")
        bot.register_next_step_handler(message, get_vacancyestimate)
    else:
        bot.send_message(message.from_user.id, "Тогда пока :)")

bot.polling()