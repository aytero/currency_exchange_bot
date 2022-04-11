import asyncio
import logging

import typing
from aiogram import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from states import Info, Editing
from core.config import settings
from core.phrases import phrases

from core.validation import validate_charset, validate_name, name_in_names

# from keyboards import get_country_keyboard
from db.data import db_dict

logging.basicConfig(level=logging.WARN)  # INFO

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
# )

logger = logging.getLogger(__name__)

loop = asyncio.get_event_loop()
bot = Bot(token=settings.BOT_TOKEN, loop=loop, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

vote_cb = CallbackData('vote', 'action', 'id')  # post:<action>:<amount>


def is_admin(name: str) -> bool:
    return name in ['TONYPONY', 'aytero']


def get_keyboard(amount, edit=False):
    t = types.InlineKeyboardMarkup()
    t.add(types.InlineKeyboardButton('Обменять наличные',    callback_data=vote_cb.new(action='new', id=amount)))
    t.add(types.InlineKeyboardButton('Курс обмена', callback_data=vote_cb.new(action='rates', id=amount)))
    return t


def add_emoji(name):
    return phrases.emoji[name] + " " + name


def get_country_keyboard():
    t = types.InlineKeyboardMarkup()
    # id = name of the country
    # idx = 0
    for country in db_dict['countries']:
        t.add(types.InlineKeyboardButton(add_emoji(country), callback_data=vote_cb.new(action='country', id=country)))
        # idx += 1
    return t


def get_city_keyboard(callback_data):
    t = types.InlineKeyboardMarkup()
    # id = name of the city
    countries = db_dict['cities']
    cities = countries[callback_data['id']]
    for city in cities:
        t.add(types.InlineKeyboardButton(city, callback_data=vote_cb.new(action='city', id=city)))
    return t


def get_currency_to_sell_keyboard():
    t = types.InlineKeyboardMarkup()
    # id = name of the currency
    for currency in db_dict['currencies']:
        t.add(types.InlineKeyboardButton(currency, callback_data=vote_cb.new(action='currency_to_sell', id=currency)))
    return t


def get_currency_to_buy_keyboard():
    t = types.InlineKeyboardMarkup()
    # id = name of the currency
    for currency in db_dict['currencies']:
        t.add(types.InlineKeyboardButton(currency, callback_data=vote_cb.new(action='currency_to_buy', id=currency)))
    return t


def get_date_keyboard():
    t = types.InlineKeyboardMarkup()
    # id = name of the currency
    for date in db_dict['date']:
        t.add(types.InlineKeyboardButton(date, callback_data=vote_cb.new(action='date', id=date)))
    return t


def get_time_keyboard():
    t = types.InlineKeyboardMarkup()
    # id = name of the currency
    for time_slot in db_dict['time_slots']:
        t.add(types.InlineKeyboardButton(time_slot, callback_data=vote_cb.new(action='time', id=time_slot)))
    return t


async def delete_msg(chat_id, msg_id):
    try:
        await bot.delete_message(chat_id, msg_id)
    except:
        print("can't delete msg")


async def set_commands(dispatcher):
    commands = [types.BotCommand(command="/start", description="refresh bot")]
    await bot.set_my_commands(commands)


@dp.errors_handler(exception=MessageNotModified)  # for skipping this exception
async def message_not_modified_handler(update, error):
    return True

welcome = (
    '- Меню -\n'
    # '- Нажмите <b>add</b>, чтобы добавить нового участника.\n'
    # '- Нажмите <b>search by location</b>, чтобы найти единомышленника по городу.\n'
    # '- Нажмите <b>search by words</b>, чтобы найти единомышленника по ключевым словам.\n'
    # '- Нажмите <b>edit</b>, чтобы редактировать свою информацию.\n'
    )


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.reply(welcome, reply_markup=get_keyboard(0), reply=False,
                        parse_mode='html'
                        )


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def create_buttons_lst(table_type) -> list:

    action = {
        'city': 'city',
        'country': 'country',
        'currency_to_sell': 'currency_to_sell',
        'amount': 'amount',
        'currency_to_buy': 'currency_to_buy',
        'time': 'time',
        'date': 'date',
        'confirm': 'confirm',
    }[table_type]

    # if rename:
    #     action = "e_" + action
    # elif search:
    #     action = "s_" + action

    btns_lst = []
    locs = db_dict[table_type]
    # locs = session.query(table_type)
    # if 'city' in action:
    #     logger.info("city in action")
    #     locs = locs.join(Countries).filter(Countries.name == country)
    for loc in locs:
        btn = types.InlineKeyboardButton(
            loc, callback_data=vote_cb.new(loc, action=action)
        )
        btns_lst.append(btn)
    return btns_lst


def create_menu(table_type=None, confirmation=False):
    btns = types.InlineKeyboardMarkup()
    if table_type:
        for couple in chunks(create_buttons_lst(table_type), 3):
            btns.row(*couple)
    if confirmation:  # TODO change var name also TODO delete unconfirmed records
        btns.row(types.InlineKeyboardButton(
            "Yes", callback_data=vote_cb.new("no", action='conf')))
    btns.row(types.InlineKeyboardButton(
            "Back", callback_data=vote_cb.new("no", action='exit')
        ))
    return btns


@dp.callback_query_handler(vote_cb.filter(action='rates'))  # , state=State.in_account)
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    await Info.info.set()
    await state.update_data(query=query)  # bot_id=callback_data.get('id'),
    await query.message.edit_text(phrases.rates_info, reply_markup=create_menu())


@dp.callback_query_handler(vote_cb.filter(action='new'))  # , state=State.in_account)
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    async with state.proxy() as data:
        await Editing.country.set()
        await state.update_data(query=query)  # bot_id=callback_data.get('id'),
        await query.message.edit_text(phrases.pick_country, reply_markup=get_country_keyboard())


COUNTRY, CITY, CURRENCY = range(3)


@dp.message_handler(state=Editing.country)
@dp.callback_query_handler(vote_cb.filter(action='country'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data:
            data['country'] = callback_data['id']

        await query.message.edit_text(
            phrases.pick_city, reply_markup=get_city_keyboard(callback_data))
        await Editing.next()


@dp.message_handler(state=Editing.city)
@dp.callback_query_handler(vote_cb.filter(action='city'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data:
            data['city'] = callback_data['id']

        # TODO sell -> amount -> buy
        await query.message.edit_text(
            phrases.pick_currency_to_sell, reply_markup=get_currency_to_sell_keyboard())
        await Editing.next()


@dp.message_handler(state=Editing.currency_to_buy)
@dp.callback_query_handler(vote_cb.filter(action='currency_to_sell'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data:
            data['currency_to_sell'] = callback_data['id']

        await query.message.edit_text(
            phrases.pick_amount, reply_markup=create_menu())
        await Editing.next()


@dp.message_handler(state=Editing.amount)
@dp.callback_query_handler(vote_cb.filter(action='amount'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')

        input_amount = message.text
        data['amount'] = input_amount

        await delete_msg(message.chat.id, message.message_id)
        await query.message.edit_text(
            phrases.pick_currency_to_buy, reply_markup=get_currency_to_buy_keyboard())
        await Editing.next()


@dp.message_handler(state=Editing.currency_to_sell)
@dp.callback_query_handler(vote_cb.filter(action='currency_to_buy'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data:
            data['currency_to_buy'] = callback_data['id']

        await query.message.edit_text(
            phrases.pick_date, reply_markup=create_menu('date'))
            # phrases.pick_date, reply_markup=get_date_keyboard())
        await Editing.next()


@dp.message_handler(state=Editing.date)
@dp.callback_query_handler(vote_cb.filter(action='date'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data:
            data['date'] = callback_data['id']

        await query.message.edit_text(
            phrases.pick_time, reply_markup=get_time_keyboard())
        await Editing.next()


# TODO do not delete the summary from the user. Make second mode without question to edit msg
def display_summary(info=None, ask=False):
    msg = f'Here is your appointment summary: \n'
    if info:
        msg += f"Страна: <b>{info['country']}</b>\n"
        msg += f"Город: <b>{info['city']}</b>\n"
        msg += f"Продать: <b>{info['amount']} {info['currency_to_sell']}</b>\n"
        # calculate according to binance rates
        msg += f"Получить: <b>{info['currency_to_buy']}</b>\n"
        msg += f"Дата и время: <b>{info['date']} {info['time']}</b>\n"
    if ask:
        msg += f'\n<b>Подтвердить?</b> \n'
    return msg


@dp.message_handler(state=Editing.time)
@dp.callback_query_handler(vote_cb.filter(action='time'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data:
            data['time'] = callback_data['id']

        info = {'country': data['country'],
                'city': data['city'],
                'currency_to_sell': data['currency_to_sell'],
                'currency_to_buy': data['currency_to_buy'],
                'amount': data['amount'],
                'date': data['date'],
                'time': data['time'],
                }

        await query.message.edit_text(
            display_summary(info, ask=True), reply_markup=create_menu(confirmation=True))
        await Editing.next()


@dp.message_handler(state=Editing.confirmation)
@dp.callback_query_handler(vote_cb.filter(action='conf'), state='*')
async def new_entry_account_manager(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        # await bot.forward_message(chat_id='aytero', from_chat_id=message.from_user.id, message_id=message.message_id)
        # await bot.send_message(message.from_user.id, "test message")
        await data.get('query').message.edit_text("Запись успешно добавлена!",
                                                  parse_mode='html',
                                                  reply_markup=get_keyboard(0),
                                                  )
        await Editing.next()


@dp.callback_query_handler(vote_cb.filter(action='exit'), state="*")  # , state=State.in_account)
async def inline_kb_creating(query: types.CallbackQuery,
                             state: FSMContext,
                             callback_data: typing.Dict[str, str]):
    await state.finish()
    await query.message.edit_text(welcome, reply_markup=get_keyboard(0),
                                  parse_mode='html'
                                  )


@dp.callback_query_handler(vote_cb.filter(action='delete'))  # , state=State.in_account)
async def inline_kb_creating(query: types.CallbackQuery,
                             state: FSMContext,
                             callback_data: typing.Dict[str, str]):
    # n = session.query(User).filter(User.id == callback_data['id']).first()
    # if n:
    #     session.delete(n)
    #     session.commit()
    await delete_msg(query.message.chat.id, query.message.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, on_startup=set_commands)  # skip_updates=True,
