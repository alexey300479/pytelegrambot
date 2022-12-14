from telebot.handler_backends import State, StatesGroup  # States


# Создаём группу состояний процесса регистрации
class RegisterStates(StatesGroup):
    # Эти два значения получаем автоматически после отправки
    # пользователем команды /start
    tg_user_id_username = State()    # 1. Идентификатор пользователя Telegram
    # tg_username = State()   # 2. Имя пользователя Telegram

    # Эти три значения получаем автоматически если
    # одновременно выполняются условия:
    # 1. Пользователь согласен поделиться контактами;
    # 2. Профиль пользователя в Telegram заполнен
    first_name = State()    # 3. Имя
    last_name = State()     # 4. Фамилия
    phone = State()        # 5. Телефон

    # Это значение запрашиваем у пользователя,
    # проверяем на соответствие правилам для
    # имен ящиков электронной почты и проводим
    # процедуру подтверждения кодом
    email = State()        # 6. Электронная почта

    # Это значение проверяем на соответствие сгенерированному и отправленному
    # четырехзначному коду подтверждения
    email_confirm = State()  # 6.1. Подтверждение электронной почты

    # Это значение проверяем на работоспособность ссылки
    socials = State()       # 7. Ссылка на страницу в соцсети

    # Это значение проверяем на соовтетствие формату даты
    # ГГГГ-ММ-ДД
    birth_date = State()    # 8. Дата рождения

    # Фото загружаем в облако со случайно сформированным
    # именем файла и ссылку на этот файл сохраняем в базе
    photo = State()         # 9. Фото

    # Предлагаем выбор из варинатов (объект Buidings модели)
    building = State()      # 10. Здание инкубатора

    # Просто текстовые значение без проверок
    office = State()        # 11. Номер офиса
    company = State()       # 12. Название компании

    # Предлагаем из вариантов (объект Branch модели)
    branch = State()        # 13. Направление бизнеса

    # Это значение проверяем на работоспособность ссылки
    website = State()       # 14. Сайт компании

    # Это значение проверяем на длину в
    description = State()   # 15. Описание бизнеса

    # Это значение означает, что процедура регистрации успешно завершена
    complete = State()
