import asyncio
from telebot.async_telebot import AsyncTeleBot  # Используем асинхронный бот
from telebot import types  # Подключили дополнения
import pandas as pd
import json

bot_name = '@BizIncubator71Bot'
with open('tobibot/api_tokens.json', 'r') as api_tokens_file:
    api_tokens = json.load(api_tokens_file)
    bot_api_token = api_tokens[bot_name]

bot = AsyncTeleBot(bot_api_token)  # Подключили токен

users_df = pd.read_csv('tobibot/data/users.csv', sep=';')


@bot.message_handler(commands=['start'])
async def start(message):
    user_id = message.from_user.id
    if user_id not in users_df['user_id'].values:
        keyboard = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True, resize_keyboard=True)

        button_phone = types.KeyboardButton(
            text="РЕГИСТРАЦИЯ", request_contact=True)
        keyboard.add(button_phone)
        text = '''
Вы еще не зарегистрированы в системе.

Я помогу сделать это быстро и удобно.

Для начала нажмите на кнопку "РЕГИСТРАЦИЯ" ниже, а затем дайте согласие на отправку ваших контактных данных.

Если ваш профиль в Telegram заполнен верно, то вам не придётся вводить имя, фамилию и номер телефона вручную.
        '''
        await bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Объявили ветку, в которой прописываем логику на тот случай, если пользователь решит прислать номер телефона :)


@bot.message_handler(content_types=['contact'])
async def contact(message):
    if message.contact is not None:  # Если присланный объект <strong>contact</strong> не равен нулю
        # Выводим у себя в панели контактные данные. А вообщем можно их, например, сохранить или сделать что-то еще.
        print(message.contact)
        await bot.send_message(message.chat.id, f'Ваше имя: {message.contact.first_name}')
        await bot.send_message(message.chat.id, f'Ваша фамилия: {message.contact.last_name}')
        await bot.send_message(message.chat.id, f'Ваш номер телефона: {message.contact.phone_number}')
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton(
            text='ДА', callback_data='right_contacts')
        button_no = types.InlineKeyboardButton(
            text='НЕТ', callback_data='wrong_contacts')
        keyboard.add(button_yes)
        keyboard.add(button_no)
        await bot.send_message(message.chat.id, 'Всё верно?', reply_markup=keyboard)


@ bot.callback_query_handler(func=lambda call: True)
async def callback_worker(call):
    if call.data == 'right_contacts':
        await bot.send_message(call.message.chat.id, 'Отлично!')
    elif call.data == 'wrong_contacts':
        await bot.send_message(call.message.chat.id, 'Видимо ваш профиль в Telegram заполнен неверно. Сожалею, придется вводить данные вручную!')


asyncio.run(bot.polling())
