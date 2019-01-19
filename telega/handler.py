import random
import string

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import ConversationHandler

import config
from clothes.models import Clothes
from users.models import User
from wardrobe import db
from wardrobe.app import create_app
from weather import Weather


# TODO fix a lot of connections
def connect_db():
    app = create_app()
    app.app_context().push()
    app.config.from_object(config.Default)
    return app


def add_clothes_start(bot, update, user_data):
    # TODO add translate
    update.message.reply_text('Write name of new clothes', reply_markup=ReplyKeyboardRemove())
    return 'name'


def add_clothes_get_name(bot, update, user_data):
    clth_name = update.message.text
    user_data["add_clothes_name"] = clth_name


    reply_keyboard = [["headdress", "outerwear", "underwear", "footwear", "scarf", "socks", "gloves", "pants", "shirt_sweaters"]]
    update.message.reply_text(
        # TODO add translate
        "Write clothes type of new clothes",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return 'clth_type'


def add_clothes_get_type(bot, update, user_data):
    clth_type = update.message.text
    user_data["add_clothes_clth_type"] = clth_type

    # TODO add translate
    update.message.reply_text('Write min temperature of new clothes')
    return 'temperature_min'


def add_clothes_get_temperature_min(bot, update, user_data):
    try:
        temperature_min = int(update.message.text)
    except ValueError:
        update.message.reply_text('Write real number')
        return 'temperature_min'

    user_data["add_clothes_temperature_min"] = temperature_min

    # TODO add translate
    update.message.reply_text('Write max temperature of new clothes')
    return 'temperature_max'


def add_clothes_get_temperature_max(bot, update, user_data):
    try:
        temperature_max = int(update.message.text)
    except ValueError:
        # TODO add translate
        update.message.reply_text('Write real number')
        return 'temperature_max'

    user_data["add_clothes_temperature_max"] = temperature_max

    username = update.message.from_user.username
    registered_user = User.query.filter(User.username == username).first()
    user_id = registered_user.id
    clothes_name = user_data['add_clothes_name']
    type = Clothes.Types.query.filter(Clothes.Types.desc == user_data['add_clothes_clth_type']).first().id
    temp_min = user_data['add_clothes_temperature_min']
    temp_max = user_data['add_clothes_temperature_max']

    new_clothes = Clothes(user_id, clothes_name, type, temp_min, temp_max)
    connect_db()
    db.session.add(new_clothes)
    db.session.commit()

    # TODO add translate
    user_text = """Add clothes {add_clothes_name} with type {add_clothes_clth_type} and temperature from {add_clothes_temperature_min} to {add_clothes_temperature_max}""".format(**user_data)
    update.message.reply_text(user_text, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def dontknow(bot, update, user_data):
    # TODO add translate
    update.message.reply_text('Try again')


def get_help(bot, update):
    text = 'I can this:\n /start\n/location <city,country>\n/add or Добавить шмотки\n/get_clothes\n/help'
    update.message.reply_text(text)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def registration_user(bot, update):
    connect_db()
    username = update.message.from_user.username
    registered_user = User.query.filter(User.username == username).first()
    if registered_user is None:
        new_user = User(username)
        password = id_generator()
        new_user.set_user_password(password)
        db.session.add(new_user)
        db.session.commit()
        # TODO add translate
        update.message.reply_text(f'You user {username} add in system, your password for website {password}')
    else:
        # TODO add translate
        update.message.reply_text(f'You user {username} already in system.')


def get_clothes(bot, update):
    connect_db()

    username = update.message.from_user.username
    user = User.query.filter(User.username == username).first()
    weather = Weather(user.geo, user.lang)

    temperature = weather.temp
    list_clothes = Clothes.query.filter(Clothes.user_id == user.id).filter(
        Clothes.temperature_min <= temperature).filter(Clothes.temperature_max >= temperature).all()

    # TODO add translate
    text = f'In {user.geo} now {temperature} °C:\n\n'
    if list_clothes:
        for one_clothes in list_clothes:
            clth_type = Clothes.Types.query.filter(Clothes.Types.id == one_clothes.clth_type).first()
            text += f'{clth_type.desc} - {one_clothes.name}\n'
    else:
        # TODO add translate
        text += 'You haven\'t clothes in the wardrobe.'

    update.message.reply_text(text)


def change_location(bot, update):
    connect_db()
    username = update.message.from_user.username
    user = User.query.filter(User.username == username).first()
    try:
        new_location = update.message.text.split(' ')[1]
    except:
        # TODO add translate
        update.message.reply_text(f'Write location pls')
        return
    db.session.query(User).filter(User.username == user.username).update({'geo': new_location})
    db.session.commit()
    # TODO add translate
    update.message.reply_text(f'Location for {username} now is {new_location}')
