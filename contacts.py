import telebot  # Подключили библиотеку Телебот - для работы с Телеграм
from telebot import types  # Подключили дополнения
import json

bot_name = '@Alexey300479Bot'
with open('api_tokens.json', 'r') as api_tokens_file:
    api_tokens = json.load(api_tokens_file)
    bot_api_token = api_tokens[bot_name]

bot = telebot.TeleBot(bot_api_token)  # Подключили токен


# Объявили ветку для работы по команде <strong>number</strong>
@bot.message_handler(commands=['number'])
def phone(message):
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True)  # Подключаем клавиатуру
    # Указываем название кнопки, которая появится у пользователя
    button_phone = types.KeyboardButton(
        text="Отправить телефон", request_contact=True)
    keyboard.add(button_phone)  # Добавляем эту кнопку
    # Дублируем сообщением о том, что пользователь сейчас отправит боту свой номер телефона (на всякий случай, но это не обязательно)
    bot.send_message(message.chat.id, 'Номер телефона', reply_markup=keyboard)


# Объявили ветку, в которой прописываем логику на тот случай, если пользователь решит прислать номер телефона :)
@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:  # Если присланный объект <strong>contact</strong> не равен нулю
        # Выводим у себя в панели контактные данные. А вообщем можно их, например, сохранить или сделать что-то еще.
        print(message.contact)


bot.infinity_polling()
