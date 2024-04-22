import requests

url = 'http://wttr.in/'

weather_parameters = {
    '0': '',
    'T': '',
    'lang': 'ru'
    }

cities = [
    'Омск',
    'Калининград',
    'Челябинск',
    'Владивосток',
    'Душанбе',
    'Москва',
    'Екатеринбург',
    'Стерлитамак',
    'Волгоград',
    'Оренбург',
     ]


def make_url(city):
    # в URL задаём город, в котором узнаем погоду
    return f'http://wttr.in/{city}'


def make_parameters():
    params = {
        'lang': 'ru',
        'format': 2,  # погода одной строкой
        'M': ''  # скорость ветра в "м/с"
    }
    return params


def what_weather(city):
    try:
        response = requests.get(make_url(city), make_parameters())
        if response.status_code == 200:
            return response.text
        else:
            return '<ошибка на сервере погоды>'
    except requests.ConnectionError:
        return '<сетевая ошибка>'
    
    
    
    # Напишите тело этой функции.
    # Не изменяйте остальной код!

print('Погода в городах:')
for city in cities:
    print(city, what_weather(city))