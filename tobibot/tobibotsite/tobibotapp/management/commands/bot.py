import os
from datetime import datetime
from pprint import pprint

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator
from telebot import TeleBot  # Используем синхронный бот
from telebot import types  # Подключили дополнения
from telebot import custom_filters
from telebot import formatting
from telebot.storage import StateRedisStorage
from tobibotapp.models import Branch, Building, Resident

from .config.config import get_config
from .lib.email import get_confirm_code, send_email
from .lib.states import RegisterStates
from .lib.validators import is_date_valid, is_email_valid, is_phone_valid

DEBUG = True


bot_name, bot_token, redis_password = get_config()
bot = TeleBot(bot_token)  # Подключили токен
state_storage = StateRedisStorage(
    password=redis_password)  # Создали хранилище состояний

# Создаём класс, для того, чтобы
# запуск бота в среде Django командой:
# python manage.py bot


class Command(BaseCommand):
    help = 'Запуск телеграм-бота'

    def handle(self, *args, **options):
        bot.add_custom_filter(custom_filters.StateFilter(bot))
        bot.infinity_polling(skip_pending=True)  # Запустили бот


# Обрабатываем команды /start и /help
@bot.message_handler(commands=['start', 'help'])
def start_help(message):
    # Отладка
    if DEBUG:
        print('start/help')

    # Если эту команду мы получили от бота, то игноририуем
    if message.from_user.is_bot:
        return

    # Если это не бот, то сразу устанавливаем в redis состояние tg_user_id_username
    # и записываем в данные tg_user_id и tg_username
    bot.set_state(
        message.from_user.id,
        RegisterStates.tg_user_id_username,
        message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['tg_user_id'] = message.from_user.id
        data['tg_username'] = message.from_user.username

    # Пытаемся получить запись с таким id из БД
    resident = Resident.objects.filter(tg_user_id=message.from_user.id).first()

    # Если такая запись есть или пользователь запросил подсказку
    if resident is not None or message.text == '/help':
        text = '''
Для поиска резидентов по направлениям бизнеса воспользуйтесь командой /catalog

Для получения информации о предстоящих событиях бизнес-инкубатора и центра "Мой Бизнес" воспользуйтесь командой /events

Для отправки обращения в службу технической поддержки воспользуйтесь командой /support

Если хотите забронировать конференцзал, класс или переговорную комнату на определенное время отправьте /book

Если хотите провести своё мероприятие при информационной поддержке бизнес-инкубатора и центра "Мой Бизнес" отправьте /propose
        '''
        bot.send_message(message.chat.id, text)
    else:
        keyboard = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True, resize_keyboard=True)

        button_reg = types.KeyboardButton(
            text="РЕГИСТРАЦИЯ", request_contact=True)
        keyboard.add(button_reg)
        text = '''
Вы еще не зарегистрированы в системе.

Я помогу сделать это быстро и удобно.

Нажмите на кнопку <<РЕГИСТРАЦИЯ>> и дайте согласие на отправку ваших контактных данных.

Если ваш профиль в Telegram заполнен верно, то вам не придётся вводить имя, фамилию и номер телефона вручную.

ВНИМАНИЕ! Нажимая на кнопку <<РЕГИСТРАЦИЯ>> вы даёте ГУ ТО "Тульский областной бизнес-инкубатор" согласие на обработку и хранение персональных данных в соответствии с законодательством РФ. 
            '''
        bot.send_message(message.chat.id, text, reply_markup=keyboard)


# Обрабатываем команду /state
@bot.message_handler(commands=['state'])
def state(message):
    bot_state = bot.get_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, f'Текущее состояние бота: {bot_state}')


# Объявили ветку, в которой прописываем логику на тот случай, если пользователь решит прислать номер телефона
@bot.message_handler(content_types=['contact'])
def contact(message):
    # Отладка
    if DEBUG:
        print('contact')

    if message.contact is not None:  # Если присланный объект contact не пустой
        if message.contact.first_name is not None\
                and message.contact.last_name is not None\
                and message.contact.phone_number is not None\
                and message.from_user.username is not None:

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
        else:
            text = '''
Ваш профиль в Telegram не оформлен должным образом.
Сожалею, но придётся ввести данные вручную.

Итак, ваше имя:
'''
            bot.set_state(
                message.from_user.id,
                RegisterStates.first_name,
                message.chat.id)

            bot.send_message(message.chat.id, text)


@bot.message_handler(state=RegisterStates.first_name)
def get_first_name(message):

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['first_name'] = message.text

    bot.set_state(
        message.from_user.id,
        RegisterStates.last_name,
        message.chat.id)

    text = '''
Ваше имя успешно сохранёно в базе 👍🏻.
Прогресс регистрации 3 из 15 🛫.

Введите вашу фамилию:
    '''

    bot.send_message(message.chat.id, text)


@bot.message_handler(state=RegisterStates.last_name)
def get_last_name(message):

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['last_name'] = message.text

    bot.set_state(
        message.from_user.id,
        RegisterStates.phone,
        message.chat.id)

    text = '''
Ваша фамилия успешно сохраена в базе 👍🏻.
Прогресс регистрации 4 из 15 🛫.

Введите ваш номер телефона:
    '''

    bot.send_message(message.chat.id, text)


@bot.message_handler(state=RegisterStates.phone)
def get_phone(message):

    if is_phone_valid(message.text):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone'] = message.text

        bot.set_state(
            message.from_user.id,
            RegisterStates.email,
            message.chat.id)

        text = '''
Ваш номер телефона успешно сохранён в базе 👍🏻.
Прогресс регистрации 5 из 15 🛫.

Теперь я попрошу у вас адрес электронной почты.

Идеально, если эта почта будет доступна всем сотрудникам
вашей организации.

Это позволит им увидеть информацию о предстоящих обучающих мероприятиях и обсудить с вами участие в них.

Новые знания для вас и ваших сотрудников очень помогут в развитии бизнеса и дадут массу новых идей 💡.

Итак, ваша почта:
        '''

    else:
        bot.set_state(
            message.from_user.id,
            RegisterStates.phone,
            message.chat.id)

        text = '''
Что-то пошло не так.

Введите номер телефона еще раз, пожалуйста:
'''

    bot.send_message(message.chat.id, text)


@bot.message_handler(state='*', commands=['cancel'])
def any_state(message):
    if DEBUG:
        report = f'''
message_handler(state='*', commands=['cancel'])
message.text: {message.text}
message.from_user.id: {message.from_user.id}
message.chat.id: {message.chat.id}
        '''
        print(report)

    bot.send_message(message.chat.id, "Регистрация отменена")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # Отладка
    if DEBUG:
        print(f'callback_worker with call.data: {call.data}')

    # Сначала отредактируем сообщение, нажатие
    # на одну из кнопок которого вызвало этот
    # обработчик для удаления кнопок
    # (чтобы больше не тыкали :)
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id)

    if is_phone_valid(call.data):
        # Если был передан номер телефона, то
        # Устанавливаем текущее значение состояния в email
        bot.set_state(
            call.from_user.id,
            RegisterStates.email,
            call.message.chat.id)

        # Записываем в redis следующие поля:
        # 1. tg_user_id
        # 2. tg_username
        # 3. first_name
        # 4. last_name
        # 5. phone
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['tg_user_id'] = call.from_user.id
            data['tg_username'] = call.from_user.username
            data['first_name'] = call.from_user.first_name
            data['last_name'] = call.from_user.last_name
            data['phone'] = call.data

        text = '''
Данные успешно сохранены в базе 👍🏻.
Прогресс регистрации 5/15 🛫.

Теперь я попрошу у вас адрес электронной почты.

Идеально, если эта почта будет доступна всем сотрудникам
вашей организации.

Это позволит им увидеть информацию о предстоящих обучающих мероприятиях и обсудить с вами участие в них.

Новые знания для вас и ваших сотрудников очень помогут в развитии бизнеса и дадут массу новых идей 💡.

Итак, ваша почта:
        '''
        bot.send_message(call.message.chat.id, text)
        # Отладка
        if DEBUG:
            report = f'''
Contacts retrieved and saved in redis.
User ID: {call.from_user.id}
Chat ID: {call.message.chat.id}
Bot state is {bot.get_state(call.from_user.id, call.message.chat.id)}
            '''
            print(report)

    elif call.data == 'wrong_contacts':
        # Если контакты неверны, то
        # Устанавливаем текущее значение состояния в first_name
        bot.set_state(
            call.from_user.id,
            RegisterStates.first_name,
            call.message.chat.id)

        # Записываем в redis следующие поля:
        # 1. tg_user_id
        # 2. tg_username

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['tg_user_id'] = call.from_user.id
            data['tg_username'] = call.from_user.username

        text = '''
Данные успешно сохранены в базе 👍🏻.
Прогресс регистрации 2/15 🛫.

Видимо ваш профиль в Telegram заполнен неверно.
Сожалею, придется ввести эти данные вручную!

Введите ваше имя:
        '''
        bot.send_message(call.message.chat.id, text)
    elif call.data == 'no_email':
        # Если нажата кнопка "ПИСЬМО НЕ ПРИШЛО"
        # Устанавливаем текущее значение состояния в email
        bot.set_state(
            call.from_user.id,
            RegisterStates.email,
            call.message.chat.id)
        text = '''
Попробуйте не вводить электронную почту вручную, а скопировать и вставить её.
Если это не поможет, то укажите другую электронную почту.
Итак, ваша почта:
        '''
        bot.send_message(call.message.chat.id, text)

    elif call.data.split()[0] == 'Building:':
        # Если пришли данные здании, то
        # устанавливаем состояние бота RegisterStates.office
        bot.set_state(
            call.from_user.id,
            RegisterStates.office,
            call.message.chat.id)

        # Получаем ID здания в таблице Building
        # и записываем его в redis
        building = int(call.data.split()[1])
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['building'] = building

        text = '''
Данные успешно сохранены в базе 👍🏻.
Прогресс регистрации 10 из 15 🛫.

Введите номер вашего офиса в бизнес-инкубаторе:
        '''
        bot.send_message(call.message.chat.id, text)

    elif call.data.split()[0] == 'Branch:':
        # Если пришли данные направления бизнеса, то
        # устанавливаем состояние бота RegisterStates.website
        bot.set_state(
            call.from_user.id,
            RegisterStates.website,
            call.message.chat.id)

        # Получаем ID направления в таблице Branch
        # и записываем его в redis
        branch = int(call.data.split()[1])
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['branch'] = branch

        text = '''
Данные успешно сохранены в базе 👍🏻.
Прогресс регистрации 13 из 15 🛫.

Отправьте ссылку на ваш сайт
(если сайта пока нет отправьте еще раз ссылку на соцсеть):
        '''
        bot.send_message(call.message.chat.id, text)

    elif call.data.split()[0] == 'Branch_to_find_residents:':
        branch_id = int(call.data.split()[1])
        if DEBUG:
            print(f'Branch ID selected: {branch_id}')

        residents = Resident.objects.filter(branch=branch_id)
        for resident in residents:
            if DEBUG:
                print(f'Resident found: {resident.company}')

            # with open(resident.photo, 'rb') as photo:
            demo_text = '''
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
            '''

            text = f'''
<b>{resident.company}</b>
<em>{resident.description}</em>

Контакты:
<b>{resident.first_name} {resident.last_name}</b>
<a href="tg://user?id={resident.tg_user_id}">Написать в Telegram</a>
<a href="tel:{resident.phone}">Позвонить: {resident.phone}</a>
<a href="mailto:{resident.email}">Отправить почту на: {resident.email}</a>
<a href="{resident.socials}">Соцсеть: {resident.socials}</a>
<a href="{resident.website}">Сайт: {resident.website}</a>
Адрес: {resident.building}, офис {resident.office}
                    '''

            if DEBUG:
                print(text)

            bot.send_photo(
                call.message.chat.id,
                resident.photo,
                caption=text,
                parse_mode='HTML')


@bot.message_handler(state=RegisterStates.email)
def get_email(message):
    # Отладка
    if DEBUG:
        report = f'''
@bot.message_handler(state=RegisterStates.email)
def get_email(message)

User ID: {message.from_user.id}
Chat ID: {message.chat.id}
        '''
        print(report)

    # Проверяем текст сообщения на соответствие правилам для адресов электронной почты
    email = message.text.strip()
    if is_email_valid(email):
        # Генерируем случайный проверочный код
        email_confirm_code = get_confirm_code()
        # Устанавливаем состояние бота в RegisterStates.email_confirm
        bot.set_state(
            message.from_user.id,
            RegisterStates.email_confirm,
            message.chat.id)

        # Получаем данные для этого пользователя и чата из redis
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            # Записываем электронную почту
            data['email'] = email
            # Записываем код подтверждения
            data['email_confirm_code'] = email_confirm_code

        # Отправляем письмо с кодом подтверждения
        send_email(
            email, 'Подтверждение электронной почты',
            email_confirm_code)

        text = '''
Отлично 👍🏻

Электронная почта сохранена в базе. 

Теперь давайте её подтвердим.

На указанную электронную почту я отправил 4-значный цифровой код.

Введите его пожалуйста. Если письмо не пришло к вам, то попробуйте посмотреть в папке "Спам".

Если его нет и там, то нажмите кнопку
<<ПИСЬМО НЕ ПРИШЛО>>
        '''
        keyboard = types.InlineKeyboardMarkup()
        # Добавляем кнопку ПИСЬМО НЕ ПРИШЛО на соответствующий случай
        button_no_email = types.InlineKeyboardButton(
            text='ПИСЬМО НЕ ПРИШЛО', callback_data='no_email')
        keyboard.add(button_no_email)

        # Отправляем текст с кнопкой
        bot.send_message(
            message.chat.id, text, reply_markup=keyboard)
    else:
        # Возвращаем бот в состояние получения электронной почты
        bot.set_state(
            message.from_user.id,
            RegisterStates.email,
            message.chat.id)

        # Просим повторить ввод электронной почты
        bot.send_message(
            message.chat.id, 'Что-то пошло не так. Введите, пожалуйста почту еще раз:')


@bot.message_handler(state=RegisterStates.email_confirm)
def email_confirm(message):
    # Отладка
    if DEBUG:
        print(f'RegisterStates.email_confirm')

    # Берем код подтверждения из redis
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        email_confirm_code = data['email_confirm_code']

        if email_confirm_code == message.text.strip():
            # Меняем код подтверждения почты на CONFIRMED
            data['email_confirm_code'] = 'CONFIRMED'

            # Устанавливаем бот в состояние RegisterStates.socials
            bot.set_state(
                message.from_user.id,
                RegisterStates.socials,
                message.chat.id)

            text = '''
Email успешно подтверждён и сохранён в базе 👍🏻.
Прогресс заполнения регистрационных даннных 6 из 15 🛫.

Пожалуйста, отправьте ссылку на вашу страницу в соцсети.

Эта ссылка  будет видна другим резидентам бизнес-инкубатора через инструмент "КАТАЛОГ".

Так потенциальным клиентам из экосистемы бизнес-инкубатора будет легче понять, чем вы можете быть им полезны.         
            '''

        else:
            # Возвращаем бот в состояние RegisterStates.email_confirm
            bot.set_state(
                message.from_user.id,
                RegisterStates.email_confirm,
                message.chat.id)

            # И просим пользователя ввести код подтверждения еще раз
            text = '''
Код подтверждения введен неверно.
Пожалуйста, введите его еще раз.
                '''

        bot.send_message(message.chat.id, text)


@bot.message_handler(state=RegisterStates.socials)
def get_socials(message):
    # Отладка
    if DEBUG:
        print(f'RegisterStates.socials')

    # Получаем URL социальной сети
    url = message.text.strip()
    if url.find('https://') == -1:
        url = f'https://{url}'

    val = URLValidator()

    try:
        val(url)
    except ValidationError:
        # Возвращаем бот в состояние RegisterStates.socials
        bot.set_state(
            message.from_user.id,
            RegisterStates.socials,
            message.chat.id)
        # Просим пользователя отправить ссылку повторно
        text = '''
С вашей ссылкой что-то не так.
Попробуйте еще раз
        '''
        bot.send_message(message.from_user.id, text)
        return

    # Иначе переводим бот в состояние RegisterStates.birth_date
    bot.set_state(
        message.from_user.id,
        RegisterStates.birth_date,
        message.chat.id)

    # Записываем данные в redis
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['socials'] = url

    # Запрашиваем у пользователя дату рождения
    text = '''
Ссылка на страницу в соцсетях успешно сохранена в базе 👍🏻.
Прогресс регистрации 7 из 15 🛫.

Пожалуйста, отправьте дату вашего рождения в формате:
ДД.ММ.ГГГГ, где:
* ДД - двухзначное число месяца (например 01, 13, 25)
* ММ - двухзначный порядковый номер месяца в году (например 01 - январь, 04 - апрель, 11 - ноябрь)
* ГГГГ - четырехзначный год (например 1979, 2004)

Пример:
30.04.1979 будет соответствовать 30 апреля 1979 года
        '''
    bot.send_message(message.chat.id, text)


@bot.message_handler(state=RegisterStates.birth_date)
def get_birth_date(message):
    # Отладка
    if DEBUG:
        print(f'RegisterStates.birth_date')

    birth_date = message.text.strip()
    # Если дата задана в верном формате
    if is_date_valid(birth_date):
        # Записываем её в redis
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['birth_date'] = birth_date

        # Переводим бот в состояние RegisterStates.photo
        bot.set_state(
            message.from_user.id,
            RegisterStates.photo,
            message.chat.id)

        # Просим отправить фотографию
        text = '''
Дата рождения успешно сохранена в базе 👍🏻.
Прогресс регистрации 8 из 15 🛫.

Пожалуйста, отправьте вашу фотографию:
    '''
        bot.send_message(message.chat.id, text)

    else:
        # Возвращаем бот в состояние RegisterStates.birth_date
        bot.set_state(
            message.from_user.id,
            RegisterStates.birth_date,
            message.chat.id)

        # Просим пользователя повторить ввод даты рождения
        text = '''
Дата рождения указана неверно.
Попробуйте еще раз, пожалуйста.
        '''
        bot.send_message(message.from_user.id, text)


@bot.message_handler(state=RegisterStates.photo, content_types=['photo'])
def get_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id=file_id)
    file_path = file_info.file_path
    file_name = file_path.split(sep='/')[-1]

    downloaded_file = bot.download_file(file_path=file_path)

    # Отладка
    if DEBUG:
        report = f'''
RegisterStates.photo
message.photo: {message.photo}
file_id: {file_id}
file_info: {file_info}
file_path: {file_path}
file_name: {file_name}
        '''
        print(report)

    service_file_path = f'media/images/{message.from_user.id}/{file_name}'

    os.makedirs(os.path.dirname(service_file_path), exist_ok=True)

    with open(service_file_path, 'wb') as photo:
        photo.write(downloaded_file)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['photo'] = service_file_path

    bot.set_state(
        message.from_user.id,
        RegisterStates.building,
        message.chat.id)

    buildings = list(Building.objects.values_list('address', flat=True))

    keyboard = types.InlineKeyboardMarkup()
    for i, building in enumerate(buildings, start=1):
        button = types.InlineKeyboardButton(
            f'{i}. {building}', callback_data=f'Building: {i}')
        keyboard.add(button)

    text = '''
Фото успешно сохранёно в базе 👍🏻.
Прогресс регистрации 9 из 15 🛫.

В каком здании инкубатора вы расположились?
    '''
    bot.send_message(
        message.chat.id, text, reply_markup=keyboard)


@bot.message_handler(state=RegisterStates.office)
def get_office(message):

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['office'] = message.text

    bot.set_state(
        message.from_user.id,
        RegisterStates.company,
        message.chat.id)

    text = '''
Офис успешно сохранён в базе 👍🏻.
Прогресс регистрации 11 из 15 🛫.

Как называется ваша компания?
    '''
    bot.send_message(message.chat.id, text)


@bot.message_handler(state=RegisterStates.company)
def get_company(message):

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['company'] = message.text

    bot.set_state(
        message.from_user.id,
        RegisterStates.branch,
        message.chat.id)

    text = '''
Название компании успешно сохранёно в базе 👍🏻.
Прогресс регистрации 12 из 15 🛫.

Выберите направление вашего бизнеса:
    '''

    branches = list(Branch.objects.values_list('name', flat=True))

    keyboard = types.InlineKeyboardMarkup()
    for i, branch in enumerate(branches, start=1):
        button = types.InlineKeyboardButton(
            f'{i}. {branch}', callback_data=f'Branch: {i}')
        keyboard.add(button)

    bot.send_message(message.chat.id, text, reply_markup=keyboard)


@bot.message_handler(commands=['find_residents'])
def find_residents(message):
    # Отладка
    if DEBUG:
        print('find_resdents')

        text = '''
Для поиска резидентов по определенному направлению бизнеса выберите его из списка ниже:
    '''

    branches = list(Branch.objects.values_list('name', flat=True))

    keyboard = types.InlineKeyboardMarkup()
    for i, branch in enumerate(branches, start=1):
        button = types.InlineKeyboardButton(
            f'{i}. {branch}', callback_data=f'Branch_to_find_residents: {i}')
        keyboard.add(button)

    bot.send_message(message.chat.id, text, reply_markup=keyboard)


@bot.message_handler(state=RegisterStates.website)
def get_website(message):
    # Отладка
    if DEBUG:
        print(f'RegisterStates.website')

    # Получаем URL сайта
    url = message.text.strip()
    if url.find('https://') == -1:
        url = f'https://{url}'

    val = URLValidator()

    try:
        val(url)
    except ValidationError:
        # Возвращаем бот в состояние RegisterStates.website
        bot.set_state(
            message.from_user.id,
            RegisterStates.website,
            message.chat.id)
        # Просим пользователя отправить ссылку повторно
        text = '''
С вашей ссылкой что-то не так.
Попробуйте еще раз
        '''
        bot.send_message(message.from_user.id, text)
        return

    # Иначе переводим бот в состояние RegisterStates.description
    bot.set_state(
        message.from_user.id,
        RegisterStates.description,
        message.chat.id)

    # Записываем данные в redis
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['website'] = url

    # Запрашиваем у пользователя описание бизнеса
    text = '''
Ссылка на ваш сайт успешно сохранена в базе 👍🏻.
Прогресс регистрации 14 из 15 🛫.

Пожалуйста, отправьте описание вашего бизнеса.
        '''
    bot.send_message(message.chat.id, text)


@bot.message_handler(state=RegisterStates.description)
def get_description(message):
    # Отладка
    if DEBUG:
        print(f'RegisterStates.description')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['description'] = message.text

    text = '''
Описание вашего бизнеса успешно сохранёно в базе 👍🏻.
Поздравляем, регистрация завершена 🚀.

Нажмите на кнопку ниже и присоединяйтесь к группе резидентов вашего здания.
Вы будете получать все новости, познакомитесь с ближайшими соседями.

Я буду помогать вам. Держать в курсе событий. Давать информацию о других резидентах.

Чтобы узнать о моих возможностях выберите в меню пункт "ПОМОЩЬ" или отправьте /help.
    '''
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['description'] = message.text

        print(f"type of data['birth_date'] is {type(data['birth_date'])}")
        if data['birth_date'] is not datetime:
            data['birth_date'] = datetime.strptime(
                data['birth_date'], '%d.%m.%Y')

        building_id = data['building']
        building = Building.objects.filter(id=building_id).first()
        data['building'] = building

        branch_id = data['branch']
        branch = Branch.objects.filter(id=branch_id).first()
        data['branch'] = branch

        data['registration_completed'] = True

        new_resident = Resident(**data)
        try:
            new_resident.save()
        except ValueError:
            bot.set_state(
                message.from_user.id,
                RegisterStates.description,
                message.chat.id)
            return

    bot.set_state(
        message.from_user.id,
        RegisterStates.complete,
        message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        building = data['building']

    tg_group_invites = list(
        Building.objects.values_list('tg_group_invite', flat=True))[building_id - 1]

    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        'Вступайте в свою группу', url=tg_group_invites)
    keyboard.add(button)

    bot.send_message(message.chat.id, text, reply_markup=keyboard)
