import json


def get_config():
    with open('tobibotapp/management/commands/config/bot_settings.json', 'r', encoding='UTF-8') as bot_settings_file:
        bot_settings = json.load(bot_settings_file)
        bot_name = bot_settings['bot_name']
        bot_token = bot_settings['bot_token']
        redis_password = bot_settings['redis_password']
        return (bot_name, bot_token, redis_password)
