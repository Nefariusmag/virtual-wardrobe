import logging
import os
from telegram.ext import Updater, CommandHandler, ConversationHandler, RegexHandler, MessageHandler, Filters
from telega.handler import id_generator, location, get, login, dontknow, add_clothes_start, add_clothes_get_name, \
    add_clothes_get_type, add_clothes_get_temperature_max, add_clothes_get_temperature_min

token = os.getenv('TOKEN', '')

PROXY = {'proxy_url': 'socks5://t1.learn.python.ru:1080',
         'urllib3_proxy_kwargs': {'username': 'learn', 'password': 'python'}}


logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


def main():
    mybot = Updater(token, request_kwargs=PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", login))
    dp.add_handler(CommandHandler("get", get))
    dp.add_handler(CommandHandler("location", location))
    # TODO /help
    add_clothes = ConversationHandler (
        entry_points=[RegexHandler('^(Добавить шмотки)$', add_clothes_start, pass_user_data=True),
                      CommandHandler('add', add_clothes_start, pass_user_data=True)],
        states={
            "name": [MessageHandler(Filters.text, add_clothes_get_name, pass_user_data=True)],
            "clth_type": [RegexHandler('^(headdress|outerwear|underwear|footwear|scarf|socks|gloves|pants|shirt_sweaters)$', add_clothes_get_type, pass_user_data=True)],
            "temperature_min": [MessageHandler(Filters.text, add_clothes_get_temperature_min, pass_user_data=True)],
            "temperature_max": [MessageHandler(Filters.text, add_clothes_get_temperature_max, pass_user_data=True)]
        },
        fallbacks=[MessageHandler(Filters.text | Filters.video | Filters.photo | Filters.document, dontknow,
                                  pass_user_data=True)]
    )
    dp.add_handler(add_clothes)

    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
