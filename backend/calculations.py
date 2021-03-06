from binanceP2P import get_price


# RUSSIA cash
# 1. Купить USDT/ВТС/ETH:
# За доллары - 103 доллара  = 100 USDT
# За рубли - курс Наличный расчет на р2р БИНАНС + 3%
#
# 2. Продать USDT/ВТС/ETH:
# За рубли - курс Наличный расчет на р2р БИНАНС - 2%
# TURKEY cash
# 1. Купить USDT/ВТС/ETH:
# За доллары - 102 доллара  = 100 USDT
# За лиры - курс Наличный расчет на р2р БИНАНС + 2%
#
# 2. Продать USDT/ВТС/ETH:
# За доллары - курс 105 USDT=100$  если <5000$
#  курс 104 USDT=100$ если >5000$
# (Биток и эфир также надо привязать + 4%)

# TODO
# Russia Карты
# 1. Купить: только USDT за рубли
# Тинькофф/сбер. Курс Тинькофф на БИНАНС + 2%.

# 2. Продать: USDT за рубли
# Курс Тинькофф на БИНАНС - 2%

card_currency = ['USDT', 'RUB']


def calculate_price_card(operation_type: str = 'BUY', cur_sell=None, cur_buy=None, amount=None) -> float:
    price = 0.0
    try:
        if operation_type == 'BUY':
            price = float(get_price(cur_buy, cur_sell, 'BUY', 'Tinkoff'))
            price += price * 0.05
            if amount and (float(amount) / price >= 5000):
                price = float(get_price(cur_buy, cur_sell, 'BUY', 'Tinkoff'))
                price += price * 0.04
        elif operation_type == 'SELL':
            price = float(get_price(cur_sell, cur_buy, 'SELL', 'Tinkoff'))
            price -= price * 0.06
            if amount and float(amount) >= 5000:
                price = float(get_price(cur_sell, cur_buy, 'SELL', 'Tinkoff'))
                price -= price * 0.05
    except:
        print('error')
    return price

# Turkey Карты
# 1. Купить USDT: только рубли с российских карт за USDT
# Карты любого банка с переводом на Тинькофф/сбер/Россельхозбанк.
# Курс Тинькофф за USDT на БИНАНС - 5% = 100$ если < 5000$
# Курс Тинькофф за USDT на БИНАНС - 4% = 100$ если > 5000$

# 2. Продать:
# Карты любого банка с переводом на Тинькофф/сбер/Россельхозбанк.
# Курс Тинькофф за USDT на БИНАНС + 6% = 100$ если < 5000$
# Курс Тинькофф за USDT на БИНАНС + 5% = 100$ если > 5000$


def calculate_price(country: str = 'Турция', operation_type: str = 'BUY',
                    cur_sell=None, cur_buy=None, amount: float = None) -> float:
    price = 0.0
    try:
        if country == 'Россия':
            if operation_type == 'BUY':
                if cur_sell == 'USD' and cur_buy == 'USDT':
                    price = 1.03
                else:
                    price = float(get_price(cur_buy, cur_sell, 'BUY', 'Tinkoff'))
                    price += price * 0.03
            if operation_type == 'SELL':
                if cur_buy == 'RUB':
                    price = float(get_price(cur_sell, cur_buy, 'SELL', 'Tinkoff'))
                    price -= price * 0.02

        if country == 'Турция':
            if operation_type == 'BUY':
                if cur_sell == 'USD' and cur_buy == 'USDT':
                    price = 1.02
                # elif cur_sell == 'TRY':
                else:
                    if cur_sell == 'TRY':
                        price = float(get_price(cur_buy, cur_sell, 'BUY', 'ziraat'))
                    else:
                        price = float(get_price(cur_buy, cur_sell, 'BUY'))
                    price += price * 0.02
            if operation_type == 'SELL':
                if cur_sell == 'USDT':
                    price = 100 / 105  # 0.95238
                    # if amount / 0.95238 < 5000:
                    #     price = 100 / 105  # 0.95238
                    # else:
                    #     price = 100 / 104  # 0.96154
                elif cur_sell in ['BTC', 'ETH']:
                    price = float(get_price(cur_sell, cur_buy, 'SELL'))
                    price -= 0.04
    except:
        print('error')
    return price


def calculate_get(amount: float = 0.0, price: float = 0.0, operation_type='SELL') -> float:
    try:
        if operation_type == 'SELL':
            total_get = amount * price
        elif operation_type == 'BUY':
            total_get = amount / price
        else:
            total_get = 0.0
    except:
        print('calculation error')
        total_get = 0.0
    return total_get


# def calculate_income(amount: float = 0.0, price: float = 0.0, fee: float = 0.0, operation_type='SELL'):
#     total_get = calculate_total_get(amount, price, fee, operation_type)
#     if operation_type == 'SELL':
#         income = amount * price - total_get
#     else:
#         income = amount / price - total_get
#     return income


# def calculate_total_get(amount: float = 0.0, price: float = 0.0, fee: float = 0.0, operation_type='SELL'):
#     # try:
#     if operation_type == 'SELL':
#         price -= price * fee
#         total_get = amount * price
#     elif operation_type == 'BUY':
#         price += price * fee
#         total_get = amount / price
#     else:
#         total_get = 0.0
#     # except:
#     # print('calculation error')
#     return total_get
