import telebot


# Our telegram bot API token is:
# 5192281587:AAEFeo7kxOUiEMehVaagOHNi9m19c6Dq5DY
# Bot: alexey-pro-bot

# You can set parse_mode by default. HTML or MARKDOWN
bot = telebot.TeleBot("5192281587:AAEFeo7kxOUiEMehVaagOHNi9m19c6Dq5DY")

name = ''
surname = ''
age = 0
user_id = 0
phone = None


@bot.message_handler(commands=['start'])
def start(msg):
    global name
    global surname
    global user_id
    global phone

    # Получаем данные отправителя
    user_id = msg.from_user.id
    name = msg.from_user.first_name

    # На старте очищаем клавиатуру
    # reply_markup = telebot.types.ReplyKeyboardRemove()
    # bot.send_message(user_id, text='Привет!', reply_markup=reply_markup)

    # Если это бот, то пишем ему: Привет, коллега и всё
    if msg.from_user.is_bot:
        bot.send_message(msg.from_user.id, 'Привет, коллега!')
        return

    surname = msg.from_user.last_name

    # if msg.from_user.is_premium:
    #     bot.send_message(user_id, text='Ты являешься премиум-пользователем')

    # if is_bot:
    #     bot.send_message(user_id, text=f'Ты являешься ботом')

    # Наша клавиатура
    keyboard = telebot.types.InlineKeyboardMarkup()

    # Кнопка Зарегистрироваться
    key_reg = telebot.types.InlineKeyboardButton(
        'Зарегистрироваться', callback_data='reg')
    keyboard.add(key_reg)

    photo_url = 'https://static.tildacdn.com/tild3564-3136-4536-a564-383333653431/shutterstock_6900122.jpg'
    bot.send_photo(
        msg.chat.id,
        photo=photo_url,
        caption='''
Добро пожаловать в мир осознанности, счаться, радости и изобилия!

В мир без суждений, проекций и ожиданий.

Мир в котором всё возможно.

Здесь нет навязанных точек зрения, осуждения за мысли,
чувтсва, эмоции, поступки.

Здесь есть только вопросы, которые создают лёгкость и расширение.

Задача проводников доступа к осознаности вдохновить тебя знать то, что ты знаешь.
        ''',
        reply_markup=keyboard
    )


@bot.message_handler(content_types=['contact'])
def contact_handler(msg):
    global phone
    if phone is None:
        phone = msg.contact.phone_number
        print(f'Телефон: {phone}')


@bot.message_handler(content_types=['text'])
def reg(msg):
    if msg.text in ['/reg', 'Зарегистрироваться']:
        bot.send_message(msg.from_user.id, 'Как тебя зовут?')
        bot.register_next_step_handler(msg, get_name)
    else:
        print(msg.text)
        bot.send_message(msg.from_user.id, 'Для регистрации напиши /reg')


def get_name(msg):
    global name
    name = msg.text
    bot.send_message(msg.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(msg, get_surname)


def get_surname(msg):
    global surname
    surname = msg.text
    bot.send_message(msg.from_user.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(msg, get_age)


def get_age(msg):
    global age
    while age == 0:
        try:
            age = int(msg.text)
        except Exception:
            bot.send_message(msg.from_user.id, 'Цифрами пожалуйста')
            bot.register_next_step_handler(msg, get_age)
            break

        if age <= 0:
            bot.send_message(
                msg.from_user.id,
                'Ваше время еще не наступило? Введи положительное число, пожалуйста'
            )
            bot.register_next_step_handler(msg, get_age)
            break

        keyboard = telebot.types.InlineKeyboardMarkup()  # Наша клавиатура

        # Кнопка Да
        key_yes = telebot.types.InlineKeyboardButton(
            text='Да',
            callback_data='yes'
        )
        keyboard.add(key_yes)

        # Кнопка Нет
        key_no = telebot.types.InlineKeyboardButton(
            text='Нет',
            callback_data='no'
        )
        keyboard.add(key_no)

        bot.send_message(
            msg.from_user.id,
            text=f'Тебя зовут {name} {surname} и тебе {age}?',
            reply_markup=keyboard
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global name
    global surname
    global phone

    if call.data == 'yes':
        # Сюда вставляем код сохранения данных или их обработки
        bot.send_message(
            call.message.chat.id,
            'Добро пожаловать в мир осознанности 🤗💫')
    elif call.data == 'reg':
        if phone is None:
            keyboard = telebot.types.InlineKeyboardMarkup()
            phone_button = telebot.types.InlineKeyboardButton(
                text="Да", request_contact=True, callback_data='reg')
            keyboard.add(phone_button)
            bot.send_message(
                call.message.chat.id, 'Поделишься контактом? Это упростит процедуру регистрации.', reply_markup=keyboard)

        elif name == '':
            bot.send_message(call.message.chat.id, 'Как тебя зовут?')
            bot.register_next_step_handler(call.message, get_name)
        elif surname == '':
            bot.send_message(call.message.chat.id, 'Какая у тебя фамилия?')
            bot.register_next_step_handler(call.message, get_surname)
        else:
            bot.send_message(call.message.chat.id, 'Сколько тебе лет?')
            bot.register_next_step_handler(call.message, get_age)
    else:
        bot.send_message(
            call.message.chat.id,
            'Отпарвь reg/ для того, чтобы зарегистрироваться заново'
        )


bot.polling(none_stop=True, interval=0)
