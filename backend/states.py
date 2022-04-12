from aiogram.dispatcher.filters.state import State, StatesGroup


class Editing(StatesGroup):
    country = State()
    city = State()
    currency_to_sell = State()
    amount = State()
    currency_to_buy = State()
    date = State()
    time = State()
    confirmation = State()
    # notify = State()


class Info(StatesGroup):
    info = State()
