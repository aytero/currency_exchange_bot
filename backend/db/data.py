
countries = ['Россия', 'Турция', 'Грузия', 'Кипр']

cities = {
    'Россия': ['Москва', 'Санкт-Петербург', 'Владимир'],
    'Турция': ['Каш', 'Стамбул', 'Анаталия', 'Калкан'],
    'Грузия': ['Тбилиси', 'Батуми'],
    'Кипр': ['Лимасол', 'Никосия'],
}

fiat = ['RUB', 'USD', 'EUR', 'TRY', 'GEL']
crypto = ['USDT', 'BTC', 'ETH', 'Other crypto']
currency = {'fiat': fiat, 'crypto': crypto}

currencies = ['RUB', 'USD', 'EUR', 'TRY', 'GEL',
              'USDT', 'BTC', 'ETH', 'Other crypto']

date = [
    '1 апреля', '2 апреля', '3 апреля',
    '4 апреля', '5 апреля', '6 апреля',
    '7 апреля', '8 апреля', '9 апреля',
    '14 апреля', '15 апреля', '16 апреля',
]

time_slots = ["8.00 - 10.00",
              "10.00 - 12.00",
              "12.00 - 14.00",
              "14.00 - 16.00",
              "16.00 - 18.00",
              ]

db_dict = {'country': countries,
           'city': cities,
           'currency_to_buy': currencies,
           'currency_to_sell': currencies,
           'date': date,
           'time': time_slots,
           'currency': currency,
           }
