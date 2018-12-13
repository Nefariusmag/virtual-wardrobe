import requests
import config


def get_external_ip():
    # todo check ping api
    return requests.get('https://api.ipify.org').text


def get_city_from_ip(ip_address):
    # todo check ping api and correct name ip
    ip_url = f'http://ip-api.com/json/{ip_address}?fields=country,city'
    result = requests.get(ip_url)
    return result.json()


def weather_by_city(city_name):
    # todo check ping api and correct type of city_name
    weather_url = "http://api.worldweatheronline.com/premium/v1/weather.ashx"
    params = {
        "key": config.API_KEY,
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


def main():
    my_external_ip = get_external_ip()
    my_city = get_city_from_ip(my_external_ip)
    weather = weather_by_city(my_city)
    temperature = weather['FeelsLikeC']
    return temperature


if __name__ == '__main__':
    main()
