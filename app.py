import requests
from flask import request, Flask, render_template

app = Flask(__name__)


class User(object):
    def __init__(self):
        self.lang = request.accept_languages[0][0]
        self.ip = self.get_user_ip()
        self.geo = self.get_user_geo()
        self.city = '{},{}'.format(self.geo['city'], self.geo['country_code2'])

    def get_user_ip(self):
        _ip = request.environ['REMOTE_ADDR']
        _ip_bit = _ip.split('.')

        if (_ip_bit[0] == '192') and (_ip_bit[1] == '168'):
            _ip = self.get_srv_ip()
        elif (_ip_bit[0] == '172') and (_ip_bit[1] in range(16, 32, 1)):
            _ip = self.get_srv_ip()
        elif _ip_bit[0] == '10':
            _ip = self.get_srv_ip()
        elif _ip_bit[0] == '127':
            _ip = self.get_srv_ip()

        return _ip

    def get_srv_ip(self):
        # todo add try to take error if api.ipify.org is not working
        _ip = requests.get('https://api.ipify.org')
        if _ip.status_code == 200:
            _ip = _ip.text

        return _ip

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
    weather = Weather(user.city, user.lang)
    return render_template('index.html', weather=str(weather), user_ip=str(user.ip), user_city=user.city)
    # weather = 'Weather: Mist, mist -11.2 92 '
    # user_ip = '46.39.56.28'
    # user_city = 'Moscow,RU'
    # return render_template('index.html', weather=str(weather), user_ip=str(user_ip), user_city=user_city)


if __name__ == '__main__':
    app.run()
