import logging
from telegram.ext import Updater, CommandHandler, ConversationHandler, RegexHandler, MessageHandler, Filters
from telega.handler import id_generator, change_location_start, change_location_get_location, get_clothes, registration_user, \
    dontknow, add_clothes_start, add_clothes_get_name, add_clothes_get_type, add_clothes_get_temperature_max, \
    add_clothes_get_temperature_min, get_help, add_clothes_get_photo
from config import PROXY_URL, TELEGRAM_TOKEN, PROXY_PASSWORD, PROXY_LOGIN

token = TELEGRAM_TOKEN

PROXY = {'proxy_url': PROXY_URL,
         'urllib3_proxy_kwargs': {'username': PROXY_LOGIN, 'password': PROXY_PASSWORD}}


logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

from wardrobe.app import create_app
import config


def connect_db():
    app = create_app()
    app.app_context().push()
    app.config.from_object(config.Default)
    return app


def main():
    mybot = Updater(token, request_kwargs=PROXY)
    dp = mybot.dispatcher

    dp.add_handler(CommandHandler("start", registration_user))
    dp.add_handler(CommandHandler("get", get_clothes))
    # dp.add_handler(CommandHandler("location", change_location))
    # TODO /help
    add_clothes = ConversationHandler(
        entry_points=[RegexHandler('^(Добавить шмотки)$', add_clothes_start, pass_user_data=True),
                      CommandHandler('add', add_clothes_start, pass_user_data=True)],
        states={
            "clth_name": [MessageHandler(Filters.text, add_clothes_get_name, pass_user_data=True)],
            "clth_type": [RegexHandler('^(headdress|outerwear|underwear|footwear|scarf|socks|gloves|pants|shirt_sweaters)$', add_clothes_get_type, pass_user_data=True)],
            "temperature_min": [MessageHandler(Filters.text, add_clothes_get_temperature_min, pass_user_data=True)],
            "temperature_max": [MessageHandler(Filters.text, add_clothes_get_temperature_max, pass_user_data=True)],
            "clth_photo": [MessageHandler(Filters.photo, add_clothes_get_photo, pass_user_data=True)]
        },
        fallbacks=[MessageHandler(Filters.text | Filters.video | Filters.photo | Filters.document, dontknow,
                                  pass_user_data=True)]
    )
    dp.add_handler(add_clothes)
    change_location = ConversationHandler(
        entry_points=[RegexHandler('^(Сменить локацию)$', change_location_start),
                      CommandHandler('location', change_location_start)],
        states={
            'get_location': [MessageHandler(Filters.text | Filters.location, change_location_get_location)]
        },
        fallbacks=[MessageHandler(Filters.text | Filters.video | Filters.photo | Filters.document, dontknow)]
    )
    dp.add_handler(change_location)
    dp.add_handler(CommandHandler('help', get_help))
    mybot.start_polling()
    mybot.idle()


app = connect_db()
if __name__ == '__main__':
    main()
