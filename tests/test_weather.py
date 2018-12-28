from weather import Weather


def test_get_weather():
    """
        Test class Weather and getting weather
    """
    test_city = 'Berlin'
    test_country = 'Germany'
    test_location = f'{test_city},{test_country}'
    test_lang = 'en'
    test_weather = Weather(test_location, test_lang)
    # test = test_weather.weather[0]
    # test1 = test_weather
    # test2 = str(test_weather)
    assert str(test_weather) != '   '

