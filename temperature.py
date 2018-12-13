import requests

API_KEY = '868ca57aa7654b2e8a0112858181312'

def get_external_ip():
    return requests.get('https://api.ipify.org').text


def get_city_from_ip(ip_address):
    # ip_url = 'http://ip-api.com/json/%s?fields=country,city' % ip_address
    ip_url = f'http://ip-api.com/json/{ip_address}?fields=country,city'
    result = requests.get(ip_url)
    return result.json()


def weather_by_city(city_name):
    weather_url = "http://api.worldweatheronline.com/premium/v1/weather.ashx"
    params = {
        "key": API_KEY,
        "q": city_name,
        "format": "json",
        "num_of_days": 1,
        "lang": "ru"
    }
    result = requests.get(weather_url, params=params)
    weather = result.json()
    if 'data' in weather:
        if 'current_condition' in weather['data']:
            try:
                return weather['data']['current_condition'][0]
            except(IndexError, TypeError):
                return False
    return False


my_external_ip = get_external_ip()
my_city = get_city_from_ip(my_external_ip)
# my_city = {'city': 'Moscow', 'country': 'Russia'}
# todo change my_city for weather can work with it
weather = weather_by_city(my_city)
temperature = weather['FeelsLikeC']
print(f'Температура за окном: {temperature}')
