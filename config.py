import os
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'postgres')
db_login = os.getenv('DB_LOGIN', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgres')
WEATHER_APIKEY = '25ca454b74082cee661317eaf1ff218d'
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'
GEOIP_URL = 'https://api.ipgeolocation.io/ipgeo'
GEOIP_APIKEY = 'e85a56721312480ebc0d0344d87f5397'
LANGUAGES = ['en', 'ru']