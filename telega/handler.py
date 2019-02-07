import random
import string

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode, KeyboardButton
from telegram.ext import ConversationHandler

from clothes.models import Clothes
from users.models import User
from wardrobe import db
from weather import Weather

import os
from config import upload_folder


def add_clothes_start(bot, update, user_data):
    # TODO add translate
    update.message.reply_text('Write name of new clothes', reply_markup=ReplyKeyboardRemove())
    return 'clth_name'


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
        # TODO add translate
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

    if temperature_max < user_data['add_clothes_temperature_min']:
        # TODO add translate
        update.message.reply_text('Maximum temperature must be greater than minimum')
        return 'temperature_max'

    user_data["add_clothes_temperature_max"] = temperature_max

    # TODO add translate
    update.message.reply_text('Send photo of new clothes')
    return 'clth_photo'


def add_clothes_get_photo(bot, update, user_data):
    from telega import app
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    os.makedirs(upload_folder, exist_ok=True)
    filename = f'{photo_file.file_id}.jpg'
    photo_file.download(os.path.join(upload_folder, filename))

    user_data["add_clothes_clth_photo"] = filename

    with app.app_context():
        username = update.message.from_user.username
        registered_user = User.query.filter(User.username == username).first()
        user_id = registered_user.id
        clothes_name = user_data['add_clothes_name']
        type = Clothes.Types.query.filter(Clothes.Types.desc == user_data['add_clothes_clth_type']).first().id
        temp_min = user_data['add_clothes_temperature_min']
        temp_max = user_data['add_clothes_temperature_max']
        photo_file = user_data["add_clothes_clth_photo"]

        new_clothes = Clothes(user_id, clothes_name, type, temp_min, temp_max, photo_file)

        db.session.add(new_clothes)
        db.session.commit()

    # TODO add translate
    user_text = """Add clothes "{add_clothes_name}" with type {add_clothes_clth_type} and temperature from {add_clothes_temperature_min} to {add_clothes_temperature_max}""".format(**user_data)
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
    from telega import app
    with app.app_context():
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
    from telega import app
    with app.app_context():
        username = update.message.from_user.username
        user = User.query.filter(User.username == username).first()
        weather = Weather(user.geo, user.lang)
        temperature = weather.temp
        try:
            color = update.message.text.split(' ')[1]
            if color not in ['red', 'green', 'blue']:
                update.message.reply_text('Now work only "red", "green", "blue"')
        except:
            color = ''
        if color == '':
            list_clothes = Clothes.query.filter(Clothes.user_id == user.id)\
                .filter(Clothes.temperature_min <= temperature)\
                .filter(Clothes.temperature_max >= temperature).all()
        else:
            from wardrobe.app import get_list_look
            list_clothes = get_list_look(color, user.id)

        # TODO add translate
        text = f'In {user.geo} now {temperature} °C.\n\n'
        update.message.reply_text(text)

        if list_clothes:
            for one_clothes in list_clothes:
                clth_type = Clothes.Types.query.filter(Clothes.Types.id == one_clothes.clth_type).first()
                text = f'{clth_type.desc} - {one_clothes.name}\n'
                update.message.reply_text(text)
                file_path = upload_folder + '/' + one_clothes.file_path
                bot.send_photo(chat_id=update.message.chat.id, photo=open(file_path, 'rb'))
        else:
            # TODO add translate
            text = 'You haven\'t clothes in the wardrobe.'
            update.message.reply_text(text)


def change_location_start(bot, update):
    location_button = KeyboardButton('Send location', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([[location_button]], one_time_keyboard=True)
    # TODO add translate
    update.message.reply_text('Write your location or send using button (if you from phone)', reply_markup=my_keyboard)
    return 'get_location'


def change_location_get_location(bot, update):
    from telega import app
    if update.message.location is not None:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim()
        location = geolocator.reverse(f'{update.message.location.latitude}, {update.message.location.longitude}')
        new_location = f'{location.raw["address"]["state"]},{location.raw["address"]["country"]}'
    else:
        new_location = update.message.text
    with app.app_context():
        username = update.message.from_user.username
        user = User.query.filter(User.username == username).first()
        db.session.query(User).filter(User.username == user.username).update({'geo': new_location})
        db.session.commit()
    # TODO add translate
    update.message.reply_text(f'Location for {username} now is {new_location}', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
