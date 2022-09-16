import json
import random
import re
from sys import path_hooks
from django.core.management.base import BaseCommand

from tobibotapp.models import Resident, Branch, Building
from telebot import types  # Подключили дополнения
from telebot import TeleBot  # Используем асинхронный бот

email_confirm_code = None

bot_name = '@BizIncubator71Bot'
with open('api_tokens.json', 'r', encoding='UTF-8') as api_tokens_file:
    api_tokens = json.load(api_tokens_file)
    bot_api_token = api_tokens[bot_name]

bot = TeleBot(bot_api_token)  # Подключили токен

email_regex = re.compile(
    r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
phone_regex = re.compile(
    r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$')


def is_email_valid(email):
    return re.fullmatch(email_regex, email)


def is_phone_valid(phone):
    return re.fullmatch(phone_regex, phone)


class Command(BaseCommand):
    help = 'Запуск телеграм-бота'

    def handle(self, *args, **options):

        # print(bot.get_me())
        bot.infinity_polling(
            timeout=10, long_polling_timeout=5)  # Запустили бот


@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.is_bot:
        return

    resident = Resident.objects.filter(tg_user_id=message.from_user.id)

    if resident.exists():
        bot.send_message(
            message.chat.id, 'Поздравляю! Вы уже зарегистрированы в системе.')
    else:
        keyboard = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True, resize_keyboard=True)

        button_phone = types.KeyboardButton(
            text="РЕГИСТРАЦИЯ", request_contact=True)
        keyboard.add(button_phone)
        text = '''
Вы еще не зарегистрированы в системе.

Я помогу сделать это быстро и удобно.

Нажмите на кнопку <<РЕГИСТРАЦИЯ>> и дайте согласие на отправку ваших контактных данных.

Если ваш профиль в Telegram заполнен верно, то вам не придётся вводить имя, фамилию и номер телефона вручную.

ВНИМАНИЕ! Нажимая на кнопку <<РЕГИСТРАЦИЯ>> вы даёте ГУ ТО "Тульский областной бизнес-инкубатор" согласие на обработку и хранение персональных данных в соответствии с законодательством РФ. 
            '''
        bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Объявили ветку, в которой прописываем логику на тот случай, если пользователь решит прислать номер телефона :)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:  # Если присланный объект <strong>contact</strong> не равен нулю
        text = f'''
Ваше имя: {message.contact.first_name}
Ваша фамилия: {message.contact.last_name}
Ваш номер телефона: {message.contact.phone_number}

Всё верно?
        '''
        keyboard = types.InlineKeyboardMarkup()
        # По нажатию кнопки "ДА" передаем номер телефона
        button_yes = types.InlineKeyboardButton(
            text='ДА', callback_data=message.contact.phone_number)
        # По нажатию кнопки "НЕТ" передаем
        button_no = types.InlineKeyboardButton(
            text='НЕТ', callback_data='wrong_contacts')
        keyboard.add(button_yes)
        keyboard.add(button_no)
        bot.send_message(message.chat.id, text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if is_phone_valid(call.data):
        # Если был передан номер телефона, то создаем объект Resident и записываем в него:
        # 1. tg_user_id
        # 2. tg_username
        # 3. first_name
        # 4. last_name
        # 5. phone
        resident = Resident(
            tg_user_id=call.from_user.id,
            tg_username=call.from_user.username,
            first_name=call.from_user.first_name,
            last_name=call.from_user.last_name,
            phone=call.data
        )
        resident.save()
        text = '''
Данные успешно сохранены в базе 👍🏻.
Прогресс регистрации 33% 🛫.

Теперь я попрошу у вас адрес электронной почты.

Идеально, если эта почта будет доступна всем сотрудникам
вашей организации.

Это позволит им увидеть информацию о предстоящих обучающих мероприятиях обсудить с вами участие в них.

Новые знания для вас и ваших сотрудников очень помогут в развитии вашего бизнеса и дадут новые идеи 💡.

Итак, ваша почта:
        '''
        message = bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(message, get_email)
    elif call.data == 'wrong_contacts':
        bot.send_message(
            call.message.chat.id, 'Видимо ваш профиль в Telegram заполнен неверно. Сожалею, придется вводить данные вручную!')


def get_email(message):
    global email_confirm_code

    # * Проверяем текст сообщения на соответствие правилам для адресов электронной почты
    email = message.text.strip()
    if is_email_valid(email):
        email_confirm_code = str(random.choice(range(1000, 10000)))
        print(email_confirm_code)

        text = '''
Отлично 👍🏻

Электронная почта сохранена в базе. 

Теперь давайте её подтвердим.

На указанную электронную почту я отправил 4-значный цифровой код.

Введите его пожалуйста:
        '''
        message_reply = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message_reply, email_confirm)
    else:
        message_reply = bot.send_message(
            message.chat.id, 'Что-то пошло не так. Введите, пожалуйста почту еще раз:')
        bot.register_next_step_handler(message_reply, get_email)


def email_confirm(message):

    if str(email_confirm_code) == message.text.strip():
        bot.send_message(
            message.chat.id, 'Поздравляю! Email успешно подтверждён.')
