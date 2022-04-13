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
    t.add(types.InlineKeyboardButton('💶 Обменять наличные',    callback_data=vote_cb.new(action='new', id=amount)))
    t.add(types.InlineKeyboardButton('Операции с картами', callback_data=vote_cb.new(action='card', id=amount)))
    t.add(types.InlineKeyboardButton('📊 Курс обмена', callback_data=vote_cb.new(action='rates', id=amount)))
    return t


async def delete_msg(chat_id, msg_id):
    try:
        await bot.delete_message(chat_id, msg_id)
    except:
        print("can't delete msg")


async def set_commands(dispatcher):
    commands = [types.BotCommand(command="/start", description="refresh bot")]
    commands = [types.BotCommand(command="/help", description="справка")]
    await bot.set_my_commands(commands)


@dp.errors_handler(exception=MessageNotModified)  # for skipping this exception
async def message_not_modified_handler(update, error):
    return True


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.reply(phrases.welcome, reply_markup=get_keyboard(0), reply=False,
                        parse_mode='html'
                        )


@dp.message_handler(commands='help')
async def cmd_start(message: types.Message):
    await message.reply(phrases.help, reply_markup=get_keyboard(0), reply=False,
                        parse_mode='html'
                        )

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def add_emoji(name, table_type):
    if 'country' in table_type:
        return phrases.emoji.get(name) + " " + name
    return name


def create_buttons_lst(table_type, data=None) -> list:

    # TODO remove this extra code
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

    btns_lst = []

    locs = db_dict[table_type]

    if 'city' in action:
        country = data.get('country')
        locs = locs.get(country)

    if 'currency' in action:
        crypto = db_dict['currency']['crypto']
        fiat = db_dict['currency']['fiat']
        locs = crypto + fiat

    # TODO fix: removes currency every iteration if 'back' pressed
    if 'currency_to_buy' in action:
        cur = data.get('currency_to_sell')
        if 'Other' not in cur:
            locs.remove(cur)

    for loc in locs:
        btn = types.InlineKeyboardButton(
            add_emoji(loc, table_type), callback_data=vote_cb.new(loc, action=action)
        )
        btns_lst.append(btn)
    return btns_lst


def create_menu(data=None, table_type=None, confirmation=False, btns_in_row=3, prev_action="exit"):
    btns = types.InlineKeyboardMarkup()
    if table_type:
        for couple in chunks(create_buttons_lst(table_type, data), btns_in_row):
            btns.row(*couple)

    if confirmation:
        btns.row(types.InlineKeyboardButton(
            "✅ Да", callback_data=vote_cb.new("no", action='conf')))

    btns.row(types.InlineKeyboardButton(
            "⬅ Назад", callback_data=vote_cb.new(action=prev_action, id='0')
            # "Назад", callback_data=vote_cb.new("no", action='back')
    ))
    btns.row(types.InlineKeyboardButton(
        "🚫 Отмена", callback_data=vote_cb.new("no", action='exit')
    ))
    return btns


# @dp.callback_query_handler(vote_cb.filter(action='back'))  # , state=State.in_account)
# async def inline_kb_creating(query: types.CallbackQuery,
#                              state: FSMContext,
#                              callback_data: typing.Dict[str, str]):
#     # await state.finish()
#     # state.reset_state()
#     await query.message.edit_text(text='backk', reply_markup=None,
#                                   parse_mode='html'
#                                   )


@dp.callback_query_handler(vote_cb.filter(action='card'))
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    await state.update_data(query=query)
    await query.message.edit_text(phrases.under_construction, reply_markup=create_menu())


@dp.callback_query_handler(vote_cb.filter(action='rates'))
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    await Info.info.set()
    await state.update_data(query=query)
    await query.message.edit_text(phrases.rates_info, reply_markup=create_menu())


@dp.callback_query_handler(vote_cb.filter(action='new'))
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    async with state.proxy() as data:
        await Editing.country.set()
        await state.update_data(query=query)
        await query.message.edit_text(phrases.pick_country,
                                      reply_markup=create_menu(table_type='country', btns_in_row=2))


# TODO switch places: cur to buy -> cur to sell -> amount
# TODO exchange rate for chosen opts
# TODO /start cmd should also reset state
# TODO something's wrong with states tho it works
def display_summary(data, ask=False, username=False, phrase=''):

    msg = f'Детали сделки: \n'
    msg += f"Страна: <b>{data.get('country', '')}</b>\n"
    msg += f"Город: <b>{data.get('city', '')}</b>\n"
    msg += f"⏩ Продать: <b>{data.get('amount', '')} {data.get('currency_to_sell', '')}</b>\n"
    # calculate according to binance rates
    msg += f"⏪ Получить: <b>{data.get('currency_to_buy', '')}</b>\n"
    msg += f"Дата и время: <b>{data.get('date', '')} {data.get('time', '')}</b>\n"
    if username:
        msg += f"Заказчик: @{data['query']['from']['username']}"
    msg += '\n'
    if ask:
        msg += f'<b>Подтвердить?</b> \n'
    return msg + phrase


@dp.message_handler(state=Editing.country)
@dp.callback_query_handler(vote_cb.filter(action='country'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['country'] = callback_data.get('id', '')

        await query.message.edit_text(
            display_summary(data=data, phrase=phrases.pick_city),
            reply_markup=create_menu(data=data, table_type='city', btns_in_row=2))
        # if callback_data and callback_data.get('id') == '0':
        #     await Editing.country.set()
        # new_state = FSMContext(storage, query.message.chat.id, query.from_user.id)
        await Editing.next()


@dp.message_handler(state=Editing.city)
@dp.callback_query_handler(vote_cb.filter(action='city'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['city'] = callback_data['id']

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_currency_to_sell, data=data),
            reply_markup=create_menu(table_type='currency_to_sell', prev_action='country'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.city.set()
        await Editing.next()


@dp.message_handler(state=Editing.currency_to_sell)
@dp.callback_query_handler(vote_cb.filter(action='currency_to_sell'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['currency_to_sell'] = callback_data['id']

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_amount, data=data), reply_markup=create_menu(prev_action='city'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.currency_to_sell.set()
        await Editing.next()
        # if callback_data and callback_data.get('id') == '0':
        #     await Editing.currency_to_sell.set()


@dp.message_handler(state=Editing.amount)
@dp.callback_query_handler(vote_cb.filter(action='amount'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')

        cur_state = await state.get_state()

        if cur_state == 'Editing:amount':
            input_amount = message.text
            if not input_amount.replace(".", "", 1).isdigit():
                await delete_msg(message.chat.id, message.message_id)
                await query.message.edit_text(
                    display_summary(phrase=phrases.err_amount, data=data), reply_markup=create_menu(prev_action='city'))
                return
            data['amount'] = message.text  # int()
            await delete_msg(message.chat.id, message.message_id)

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_currency_to_buy, data=data),
            reply_markup=create_menu(data=data, table_type='currency_to_buy', prev_action='currency_to_sell'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.amount.set()
        await Editing.next()


@dp.message_handler(state=Editing.currency_to_buy)
@dp.callback_query_handler(vote_cb.filter(action='currency_to_buy'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['currency_to_buy'] = callback_data['id']

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_date, data=data),
            reply_markup=create_menu(table_type='date', prev_action='amount'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.currency_to_buy.set()
        await Editing.next()


@dp.message_handler(state=Editing.date)
@dp.callback_query_handler(vote_cb.filter(action='date'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['date'] = callback_data['id']

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_time, data=data),
            reply_markup=create_menu(table_type='time', btns_in_row=1, prev_action='currency_to_buy'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.date.set()
        await Editing.next()


@dp.message_handler(state=Editing.time)
@dp.callback_query_handler(vote_cb.filter(action='time'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['time'] = callback_data['id']

        await query.message.edit_text(
            display_summary(data=data, ask=True), reply_markup=create_menu(confirmation=True, prev_action='date'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.time.set()
        await Editing.next()

admin_id = '249747747'  # aytero


@dp.message_handler(state=Editing.confirmation)
@dp.callback_query_handler(vote_cb.filter(action='conf'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):

    async with state.proxy() as data:

        query = data.get('query')

        await delete_msg(query.message.chat.id, query.message.message_id)

        await bot.send_message(query.from_user.id, phrases.success, parse_mode='html')
        await bot.send_message(query.from_user.id, display_summary(data), parse_mode='html')

        await bot.send_message(chat_id=admin_id, text=display_summary(data, username=True), parse_mode='html')

        await bot.send_message(message.from_user.id, phrases.welcome, reply_markup=get_keyboard(0))

        if callback_data and callback_data.get('id') == '0':
            await Editing.confirmation.set()
        # await Editing.next()
        await state.finish()


@dp.callback_query_handler(vote_cb.filter(action='exit'), state="*")
async def inline_kb_creating(query: types.CallbackQuery,
                             state: FSMContext,
                             callback_data: typing.Dict[str, str]):
    await state.finish()
    # await state.
    # await state.reset_state()
    await query.message.edit_text(phrases.welcome, reply_markup=get_keyboard(0),
                                  parse_mode='html'
                                  )


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, on_startup=set_commands)  # skip_updates=True,
