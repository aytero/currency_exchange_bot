from datetime import date, timedelta
from babel.dates import format_date


dates = [format_date((date.today() + timedelta(days=i)), 'd MMMM', locale='ru') for i in range(12)]


time_slots = ["8.00 - 10.00",
              "10.00 - 12.00",
              "12.00 - 14.00",
              "14.00 - 16.00",
              "16.00 - 18.00",
              ]


all_fiat = ['RUB', 'USD', 'EUR', 'TRY', 'GEL', 'AMD']
all_crypto = ['USDT', 'BTC', 'ETH', 'Other crypto']

db_dict = {
    'date': dates,
    'time': time_slots,
    'all_fiat': all_fiat,
    'all_crypto': all_crypto,
    'card_currency': ['USDT', 'RUB'],
    'bank': ['Тинькофф', 'Сбербанк', 'Россельхозбанк'],
    'country': {
        'Россия': {
            'city': ['Москва', 'Санкт-Петербург', 'Казань',
                     'Екатеринбург', 'Краснодар', 'Чебоксары',
                     'Йошкар-Ола', 'Нижний Новгород'],
            'currency': {
                'fiat': ['RUB', 'USD'],
                'crypto': ['USDT', 'BTC', 'ETH'],
            },
            'fee': 0,
        },
        'Турция': {
            'city': ['Анаталия', 'Каш', 'Калкан', 'Фетхие', 'Кемер'],
            'currency': {
                'fiat': ['TRY', 'USD'],
                'crypto': ['USDT', 'BTC', 'ETH'],
            },
            'fee': 0.07,
        },
        'Кипр': {
            'city': ['Ларнака', 'Лимасcол'],
            'currency': {
                'fiat': ['USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.11,
        },
        'ОАЭ': {
            'city': ['Дубай'],
            'currency': {
                'fiat': ['USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.0,
        },
        'Испания': {
            'city': ['Барселона'],
            'currency': {
                'fiat': ['USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.0,
        },
        'Индия': {
            'city': ['Гоа, Панаджи'],
            'currency': {
                'fiat': ['USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.0,
        },
        'Черногория': {
            'city': ['Подгорица'],
            'currency': {
                'fiat': ['USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.0,
        },
        'Казахстан': {
            'city': ['Алматы', 'Астана'],
            'currency': {
                'fiat': ['USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.0,
        },
        'Кыргызстан': {
            'city': ['Бишкек'],
            'currency': {
                'fiat': ['USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.0,
        },
        # 'Грузия': {
        #     'city': ['Тбилиси', 'Батуми'],
        #     'currency': {
        #         'fiat': ['GEL', 'USD', 'EUR'],
        #         'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
        #     },
        #     'fee': 0,
        # },
        # 'Армения': {
        #     'city': ['Ереван', 'Гюмри'],
        #     'currency': {
        #         'fiat': ['AMD', 'USD', 'EUR'],
        #         'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
        #     },
        #     'fee': 0,
        # },
    }
}


def filter_data(action='country', country='Турция', operation_type='BUY'):

    if 'card_currency_buy' in action:
        if operation_type == 'BUY':
            locs = ['USDT']
        else:
            locs = ['RUB']
        return locs
    if 'card_currency_sell' in action:
        locs = db_dict['card_currency']
        return locs
    if 'bank' in action:
        locs = db_dict['bank']
        return locs

    if 'country' in action:
        locs = list(db_dict.get('country').keys())
        return locs

    if 'city' in action:
        locs = db_dict['country'][country]['city']

    elif 'currency_to_sell' in action:
        fiat = db_dict['country'][country]['currency']['fiat']
        crypto = db_dict['country'][country]['currency']['crypto']
        locs = fiat + crypto

    elif 'currency_to_buy' in action:
        if operation_type == 'BUY':
            locs = db_dict['country'][country]['currency']['crypto']
        else:
            if country == 'Россия':
                locs = ['RUB']
            elif country == 'Турция':
                locs = ['USD']
            else:
                locs = db_dict['country'][country]['currency']['fiat']
    elif 'fee' in action:
        locs = db_dict['country'][country]['fee']
    else:
        locs = db_dict.get(action)
    return locs


# state_data = {
#     'query': {
#         "id": "1072658408235970412",
#         "from": {
#             "id": 249747747,
#             "is_bot": False,
#             "first_name": "Ася",
#             "username": "aytero",
#             "language_code": "en"
#         },
#         "message": {
#             "message_id": 2043,
#             "from": {"id": 5163366187, "is_bot": True, "first_name": "Dummy", "username": "dummy_dum_bot"},
#             "chat": {"id": 249747747, "first_name": "Ася", "username": "aytero", "type": "private"},
#             "date": 1650117737,
#             "text": "- Меню -",
#             "reply_markup": {"inline_keyboard": [[{"text": "💶 Операции с наличными", "callback_data": "vote:new:0"}],
#                                                  [{"text": "Операции с картами", "callback_data": "vote:card:0"}],
#                                                  [{"text": "💱 Курс обмена", "callback_data": "vote:rates:0"}]]}},
#         "chat_instance": "5285086080367001397", "data": "vote:new:0"
#     },
#     'country': 'Турция',
#     'city': 'Каш',
#     'currency_to_sell': 'TRY',
#     'operation_type': 'BUY',
#     'currency_to_buy': 'USDT',
#     'price': '14.70',
#     'amount': '200',
#     'date': '23 апреля',
#     'time': '14.00 - 16.00'
# }
