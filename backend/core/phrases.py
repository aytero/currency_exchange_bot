# from ..binanceP2P import get_price
from db.data import db_dict
from binanceP2P import get_price


def calculate_fee(price=0, country='Турция'):
    fee = db_dict['country'][country]['fee']
    return float(price) - float(price) * float(fee)


def display_summary(data, ask=False, username=False, phrase=''):

    msg = f'Детали сделки: \n'
    msg += f"Страна: <b>{data.get('country', '')}</b>\n"
    msg += f"Город: <b>{data.get('city', '')}</b>\n"
    msg += f"⏩ Продать: <b>{data.get('amount', '')} {data.get('currency_to_sell', '')}</b>\n"

    price = data.get('price')
    if price:
        price = calculate_fee(price, data.get('country'))
    if price and data.get('amount'):
        if data.get('operation_type') == 'SELL':
            calc_amount = round(float(data.get('amount')) * float(price), 4)
        else:
            calc_amount = round(float(data.get('amount')) / float(price), 8)
            # f'{a:.20f}'
        msg += f"⏪ Получить: <b>{calc_amount:.9f} {data.get('currency_to_buy', '')}</b>\n"
    if price and data.get('operation_type') == 'SELL':
        msg += f"💱 Курс: <b>1 {data.get('currency_to_sell')} = {price} {data.get('currency_to_buy')}</b>\n"
        # msg += f"Комиссия: <b>1 {price} {data.get('currency_to_buy')}</b>\n"
    elif price and data.get('operation_type') == 'BUY':
        msg += f"💱 Курс: <b>1 {data.get('currency_to_buy')} = {price} {data.get('currency_to_sell')}</b>\n"
    else:
        msg += f"⏪ Получить: <b>{data.get('currency_to_buy', '')}</b>\n"

    msg += f"Дата и время: <b>{data.get('date', '')} {data.get('time', '')}</b>\n"
    if username:
        msg += f"Заказчик: @{data['query']['from']['username']}\n"
        # msg += f"Комиссия: <b>7%</b>\n"
        # msg += f"Доход: <b>calc_amount - amount</b>\n"

    msg += '\n'
    if ask:
        msg += f'<b>Подтвердить?</b> \n'
    return msg + phrase


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
    success = 'Сделка успешно зафиксирована!\nДальше с вами свяжется человек.'

    # "✔️✅ Да", callback_data = vote_cb.new("no", action='conf')))


phrases = Phrases()
