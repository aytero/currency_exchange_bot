# from db.data import db_dict
# from aiogram import types
# from b import vote_cb


def get_country_keyboard():
    t = types.InlineKeyboardMarkup()
    # id = index of country
    idx = 0
    for country in db_dict['countries']:
        t.add(types.InlineKeyboardButton(country, callback_data=vote_cb.new(action='c_city', id=idx)))
        idx += 1
    return t
