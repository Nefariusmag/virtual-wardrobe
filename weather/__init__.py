import requests


class Weather(object):
    def __init__(self, city='Moscow,ru', lang='en'):
        self._city = city
        self._lang = lang
        self.conditions = 'Error caught'
        self.icon_weather = '01d'
        self.temp = 'Err'
        self.humidity = 'Err'
        self.wind = {'speed': 'Err', 'deg': 'Err', 'dir': 'Err'}

        self.get_weather()

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

            _conditions, _icon, _temp, _humidity, _wind = '', '', '', '', {}

            if 'weather' in _weather:
                for data in _weather['weather']:
                    _conditions = data["description"].capitalize()
                    _icon = data['icon']
            if 'main' in _weather:
                _temp = _weather['main']['temp_max']
                _humidity = _weather['main']['humidity']
            if 'wind' in _weather:
                _wind = _weather['wind']
                _wind_directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW',
                                    'NW', 'NNW']
                if _wind['deg'] < 0:
                    _wind['deg'] += 180
                _wind.update({'dir': _wind_directions[int(_wind['deg'] // 22.5)]})

                self.conditions = _conditions
                self.icon_weather = _icon
                self.temp = _temp
                self.humidity = _humidity
                self.wind = _wind

    def __str__(self):
        return '{}. {} °C, {} %, {} m/s {} ({}°)'.format(self.conditions,
                                                      self.temp,
                                                      self.humidity,
                                                      self.wind['speed'],
                                                      self.wind['dir'],
                                                      self.wind['deg'])
