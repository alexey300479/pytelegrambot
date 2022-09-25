import datetime
import re


def is_email_valid(email):
    email_regex = re.compile(
        r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    return re.fullmatch(email_regex, email)


def is_phone_valid(phone):
    phone_regex = re.compile(
        r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$')

    return re.fullmatch(phone_regex, phone)


def is_date_valid(date):
    try:
        datetime.datetime.strptime(date, '%d.%m.%Y')
    except ValueError:
        return False

    return True
