from db.data import db_dict, filter_data


def calculate_income(amount: float = 0.0, price: float = 0.0, fee: float = 0.0, operation_type='SELL'):
    a = 0
    total_get = calculate_total_get(amount, price, fee, operation_type)
    if operation_type == 'SELL':
        income = amount * price - total_get
    else:
        income = amount / price - total_get
    return income


def calculate_total_get(amount: float = 0.0, price: float = 0.0, fee: float = 0.0, operation_type='SELL'):
    # try:
    if operation_type == 'SELL':
        price -= price * fee
        total_get = amount * price
    elif operation_type == 'BUY':
        price += price * fee
        total_get = amount / price
    else:
        total_get = 0.0
    # except:
    # print('calculation error')
    return total_get


def display_summary(data, ask=False, username=None, phrase=''):
    msg = f'Детали сделки: \n'

    country = data.get('country', '')
    currency_to_sell = data.get('currency_to_sell', '')
    amount = data.get('amount', '')

    msg += f"Страна: <b>{country}</b>\n"
    msg += f"Город: <b>{data.get('city', '')}</b>\n"
    msg += f"⏩ Продать: <b>{amount} {currency_to_sell}</b>\n"

    price = data.get('price')
    operation_type = data.get('operation_type', '')
    currency_to_buy = data.get('currency_to_buy', '')
    if price:
        fee = filter_data(action='fee', country=country)
        if amount:
            total_get = calculate_total_get(float(amount), float(price), float(fee), operation_type)
            msg += f"⏪ Получить: <b>{total_get:.6f} {currency_to_buy}</b>\n"

        if operation_type == 'SELL':
            price = float(price) - float(price) * float(fee)
            msg += f"💱 Курс: <b>1 {currency_to_sell} = {price:.6f} {currency_to_buy}</b>\n"
        elif operation_type == 'BUY':
            price = float(price) + float(price) * fee
            msg += f"💱 Курс: <b>1 {currency_to_buy} = {float(price):.6f} {currency_to_sell}</b>\n"
    else:
        msg += f"⏪ Получить: <b>{currency_to_buy}</b>\n"

    msg += f"Дата и время: <b>{data.get('date', '')} {data.get('time', '')}</b>\n"
    if username:
        msg += f"Заказчик: @{username}\n"
        # exception danger float()
        fee = filter_data(action='fee', country=country)
        income = calculate_income(float(amount), float(price), float(fee), operation_type)
        msg += f"Комиссия: <b>{float(fee * 100):.2f}%</b>\n"
        msg += f"Доход: <b>{float(income):.3f} {currency_to_buy}</b>\n"

    msg += '\n'
    if ask:
        msg += f'<b>Подтвердить?</b> \n'

    return msg + phrase


def add_emoji(name, action):
    if 'country' in action:
        return phrases.emoji.get(name, '') + " " + name
    return name


class Phrases:
    welcome = (
        '- Меню -\n'
    )

    help = (
        f'<b>Бот-криптообменник</b>\n\n'
        f'- Вы можете <b>создать новую сделку</b>.\n'
        f'Заполните всю информацию, а дальше с вами свяжется оператор.\n\n'
        f'- Нажмите <b>Курс обмена</b>, чтобы посмотреть подробную информацию.\n'
        f'Курс и коммисия зависят от страны и объёма транзакции.'
    )
    rates_info = (
        '- <b>Курс обмена</b> -\n'
        '\n'
        f'<b>🌐 BTC = 43’500, 00$ 🔻4, 10 %</b>\n'
        f'<b>💠 ETH = 3’230, 00$ 🔻3, 78 %</b>\n'
        '\n'
        f'<b>💵 USDT > $ (cash)</b>\n'
        # escape '<' -> &lt; '>' -> &gt
        f'104, 50 USDT = 100$ &lt 5000$ (4, 5 %)\n'
        f'104, 00 USDT = 100$ &gt 5000$ (4 %)\n'
        '\n'
        '\n<b>💶 USDT &gt€ (cash)</b>\n'
        '116, 00 USDT = 100€ &lt 5000€ (5 %)\n'
        '114, 00 USDT = 100€ &gt 5000€ (4 %)'
        '\n'
        '\n<b>💳 ₽ &gt $ (cash)🔺🔺🔺</b>\n'
        '10’153, 00 ₽ (Russian card &gt Sber / Tinkoff) &gt 100$\n'
        '11’168, 00 ₽ (Russian card &gt Sber / Tinkoff) &gt 100€\n'
    )

    pick_country = '🌏 <b>Выберите страну</b>:'
    pick_city = f'🏙 <b>Выберите город</b>:'
    # err_input = f'Неверный ввод, попробуйте еще раз'
    pick_currency_to_sell = f'Выберите валюту, которую вы хотите <b>продать</b>: ⏩'
    pick_currency_to_buy = f'Выберите валюту, которую вы хотите <b>купить</b>: ⏪'
    pick_date = f'📆 <b>Выберите дату</b>:'
    pick_time = f'🕓 <b>Выберите время</b>:'
    pick_amount = f'Напишите <b>сумму</b>, которую вы хотите продать: 🔽️'
    err_amount = f'Неверный ввод! Введите только число. \n<b>Сумма</b>, которую вы хотите продать:'
    emoji = {'Турция': '🇹🇷',
             'Россия': '🇷🇺',
             'Грузия': '🇬🇪',
             'Армения': '🇦🇲',
             'Кипр': '🇨🇾',
             }
    under_construction = '🚧 under construction 🚧'
    back = '⬅ назад'
    cancel = '🚫 отмена'
    yes = '✔️ Да'
    exchange_cash = '💶 Операции с наличными'
    card = 'Операции с картами'
    exchange_rates = '💱 Курс обмена'
    success = 'Сделка успешно зафиксирована!\nС вами свяжется оператор.'

    # "✔️✅ Да", callback_data = vote_cb.new("no", action='conf')))


phrases = Phrases()
