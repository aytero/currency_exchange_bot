
class Phrases:
    rates_info = (
        '- <b>Exchange rates</b> -\n'
        '\n'
        f'<b>🌐 BTC = 43’500, 00$ 🔻4, 10 %</b>\n'
        f'<b>💠 ETH = 3’230, 00$ 🔻3, 78 %</b>\n'
        '\n'
        f'<b>💵 USDT > $ (cash)</b>\n'
        # escape '<'
        # f'104, 50 USDT = 100$ < 5000$ (4, 5 %)\n'
        # f'104, 00 USDT = 100$ > 5000$ (4 %)\n'
        # '\n💶 USDT >€ (cash)\n'
        # '116, 00 USDT = 100€ < 5000€ (5 %)\n'
        # '114, 00 USDT = 100€ > 5000€ (4 %)'
        # '\n💳 ₽ > $ (cash)🔺🔺🔺\n'
        # '10’153, 00 ₽ (Russian card > Sber / Tinkoff) > 100$\n'
        # '11’168, 00 ₽ (Russian card > Sber / Tinkoff) > 100€\n'
    )

    pick_country = 'Выберите страну:'
    pick_city = 'Выберите город:'
    # err_input = f'Неверный ввод, попробуйте еще раз'
    pick_currency_to_sell = f'Выберите валюту, которую вы хотите <b>продать</b>:'
    pick_currency_to_buy = f'Выберите валюту, которую вы хотите <b>купить</b>:'
    pick_date = f'📆 Выберите дату:'
    pick_time = f'🕓 Выберите время:'
    pick_amount = f'Напишите <b>сумму</b>, которую вы хотите продать:'
    confirmation_text = f'Confirm action:'
    # request_text = f'Provide date and time'
    # err_city = f'Incorrect input, enter again'
    emoji = {'Турция': '🇹🇷',
             'Россия': '🇷🇺',
             'Грузия': '🇬🇪',
             }
    under_construction = '🚧 under construction 🚧'
    back = '⬅ назад'
    success = 'Запись успешно добавлена!\nДальше с вами свяжется человек.'


phrases = Phrases()
