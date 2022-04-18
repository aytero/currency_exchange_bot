from aiogram.dispatcher.filters.state import State, StatesGroup


class Editing(StatesGroup):
    country = State()
    city = State()
    currency_to_sell = State()
    currency_to_buy = State()
    amount = State()
    date = State()
    time = State()
    confirmation = State()


class Cards(StatesGroup):
    bank = State()
    currency_to_sell = State()
    currency_to_buy = State()
    amount = State()
    confirmation = State()


class Info(StatesGroup):
    info = State()
