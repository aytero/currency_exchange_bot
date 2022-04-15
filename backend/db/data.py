from datetime import date, timedelta
import locale


locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

dates = [(date.today() + timedelta(days=i)).strftime('%d %B') for i in range(12)]

# dates = [
#     '14 апреля', '15 апреля', '16 апреля',
#     '17 апреля', '18 апреля', '19 апреля',
#     '20 апреля', '21 апреля', '22 апреля',
#     '23 апреля', '24 апреля', '25 апреля',
# ]


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
    'country': {
        'Россия': {
            'city': ['Москва', 'Санкт-Петербург', 'Владимир'],
            'currency': {
                'fiat': ['RUB', 'USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0,
        },
        'Турция': {
            'city': ['Каш', 'Стамбул', 'Анаталия', 'Калкан'],
            'currency': {
                'fiat': ['TRY', 'USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.07,
        },
        'Грузия': {
            'city': ['Тбилиси', 'Батуми'],
            'currency': {
                'fiat': ['GEL', 'USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0,
        },
        'Армения': {
            'city': ['Ереван', 'Гюмри'],
            'currency': {
                'fiat': ['AMD', 'USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0,
        },
        'Кипр': {
            'city': ['Лимасол', 'Никосия'],
            'currency': {
                'fiat': ['USD', 'EUR'],
                'crypto': ['USDT', 'BTC', 'ETH', 'Other crypto'],
            },
            'fee': 0.11,
        },
    }
}


def filter_data(data=None, action='country'):

    locs = []
    country = ''

    if 'country' in action:
        locs = list(db_dict.get('country').keys())
        return locs
    if data:
        country = data.get('country', 'Россия')
    if 'city' in action:
        locs = db_dict['country'][country]['city']

    elif 'currency_to_sell' in action:
        fiat = db_dict['country'][country]['currency']['fiat']
        crypto = db_dict['country'][country]['currency']['crypto']
        locs = fiat + crypto

    elif 'currency_to_buy' in action:
        if data.get('operation_type') == 'BUY':
            locs = db_dict['country'][country]['currency']['crypto']
        else:
            locs = db_dict['country'][country]['currency']['fiat']
    else:
        locs = db_dict.get(action)
    return locs


if __name__ == '__main__':

    # current_date = date.today().isoformat()
    # days_after = (date.today() + timedelta(days=12)).isoformat()

    # print("\nCurrent Date: ", current_date)
    # print("30 days after current date : ", days_after)
    dates = []
    # for i in range(12):
    #     dates.append((date.today()+timedelta(days=i)).strftime('%d %B'))
    # dates.append((date.today() + timedelta(days=i)).isoformat())
    dates = [(date.today() + timedelta(days=i)).strftime('%d %B') for i in range(12)]
    print(dates)
