import logging
from telegram.ext import Updater, CommandHandler, ConversationHandler, RegexHandler, MessageHandler, Filters
from telega.handler import id_generator, change_location_start, change_location_get_location, get_clothes, registration_user, \
    dontknow, add_clothes_start, add_clothes_get_name, add_clothes_get_type, add_clothes_get_temperature_max, \
    add_clothes_get_temperature_min, get_help, add_clothes_get_photo
from config import PROXY_URL, TELEGRAM_TOKEN, PROXY_PASSWORD, PROXY_LOGIN
from telegram.ext import messagequeue as mq
from datetime import time

token = TELEGRAM_TOKEN

PROXY = {'proxy_url': PROXY_URL,
         'urllib3_proxy_kwargs': {'username': PROXY_LOGIN, 'password': PROXY_PASSWORD}}


logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

from wardrobe.app import create_app
import config


@mq.queuedmessage
def start_get_clothes(bot, job):
    get_clothes(bot, job.context)


def send_clothes(bot, update, args, job_queue):
    try:
        list_schedule_time_str = str(args[0]).split(':')
        list_schedule_time_int = list(map(int, list_schedule_time_str))
        schedule_time = time(list_schedule_time_int[0], list_schedule_time_int[1])
        # TODO add save in db
        job_queue.run_daily(start_get_clothes, time=schedule_time, context=update)
        update.message.reply_text(f'Add your schedule in {list_schedule_time_int[0]}:{list_schedule_time_int[1]}')
        # new_job = job_queue.run_daily(start_get_clothes, time=schedule_time, context=update)
        # my_jobs.append(new_job)
    except (IndexError, ValueError):
        update.message.reply_text("Write time after /reminder")


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

    mybot.bot._msg_queue = mq.MessageQueue()
    mybot.bot._is_messages_queued_default = True

    dp.add_handler(CommandHandler("reminder", send_clothes, pass_args=True, pass_job_queue=True))
    mybot.start_polling()
    mybot.idle()


app = connect_db()
if __name__ == '__main__':
    # my_jobs = []
    main()
