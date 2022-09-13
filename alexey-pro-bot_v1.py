import telebot


# Our telegram bot API token is:
# 5192281587:AAEFeo7kxOUiEMehVaagOHNi9m19c6Dq5DY
# Bot: alexey-pro-bot

# You can set parse_mode by default. HTML or MARKDOWN
bot = telebot.TeleBot("5192281587:AAEFeo7kxOUiEMehVaagOHNi9m19c6Dq5DY")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if 'привет' in message.text.lower():
        bot.send_message(
            message.from_user.id,
            'Привет, чем я могу тебе помочь?'
        )
    elif message.text == '/help':
        bot.send_message(
            message.from_user.id,
            'Напиши привет'
        )
    else:
        bot.send_message(
            message.from_user.id,
            'Я тебя не понимаю. Напиши /help.'
        )


bot.polling(none_stop=True, interval=0)
