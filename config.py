import os
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'postgres')
db_login = os.getenv('DB_LOGIN', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgres')
WEATHER_APIKEY = os.getenv('WEATHER_APIKEY', '')
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'
GEOIP_URL = 'https://api.ipgeolocation.io/ipgeo'
GEOIP_APIKEY = os.getenv('GEOIP_APIKEY', '')
LANGUAGES = ['en', 'ru']


class Default:
    TESTING = False
    DEBUG = False
    SECRET_KEY = 'SECRET__K'
    # SERVER_NAME = '127.0.0.1:5000'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///simple.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Debug(Default):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

