import requests
# import json
# import flask
from flask import request, Flask

app = Flask(__name__)


class User(object):
    def __init__(self):
        self.lang = request.accept_languages[0][0]
        self.ip = request.environ['REMOTE_ADDR']
        self.geo = self.get_user_geo()

    def get_user_geo(self):
        from config import GEOIP_APIKEY, GEOIP_URL
        params = {
            'apiKey': GEOIP_APIKEY,
            'ip': self.ip
        }
        user_geo = requests.get(GEOIP_URL, params)

        if user_geo.status_code == 200:
            user_geo = user_geo.json()

        return user_geo

    class Weather(object):
            def __init__(self, city='Moscow,ru', lang='en'):
                self._city = city
                self._lang = lang
                self.weather = self.get_weather()

            def get_weather(self):
                from config import WEATHER_APIKEY, WEATHER_URL
                params = {
                    'q': self._city,
                    'APPID': WEATHER_APIKEY,
                    'units': 'metric',
                    'lang': self._lang
                }
                _weather = requests.get(WEATHER_URL, params)

                if _weather.status_code == 200:
                    _weather = _weather.json()

                conditions, temp, humidity = '', '', ''

                if 'weather' in _weather:
                    for data in _weather['weather']:
                        conditions = f'{conditions} {data["main"]}, {data["description"]}'
                if 'main' in _weather:
                    temp = _weather['main']['temp']
                    humidity = _weather['main']['humidity']

                result = (conditions, temp, humidity, )
                return result

            def __dict__(self):
                _weather = self.weather
                _weather_cats = ['conditions', 'temp', 'humidity']
                weather_dict = []
                for index in list(range(len(_weather_cats))):
                    weather_dict.append([_weather_cats[index], _weather[index]])

                return dict(weather_dict)

            def __str__(self):
                _weather = self.weather
                weather_str = ''
                for data in _weather:
                    weather_str += f'{str(data)} '

                return weather_str


@app.route('/')
def hello_world():
    user = User()
    _weather = user.Weather('Moscow,ru', user.lang)
    return str(_weather) + str(user.ip)


if __name__ == '__main__':
    app.run()
