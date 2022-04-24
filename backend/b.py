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

from states import Info, Editing, Cards
from core.config import settings
from core.phrases import phrases, add_emoji, display_summary, card_summary
from core.validation import validate_amount

# from keyboards import get_country_keyboard
from db.data import db_dict, filter_data

from calculations import calculate_price, calculate_price_card


logging.basicConfig(filename='logs/exchange_bot.log', level=logging.WARN)  # INFO

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


def get_keyboard(amount):
    t = types.InlineKeyboardMarkup()
    t.add(types.InlineKeyboardButton(phrases.exchange_cash, callback_data=vote_cb.new(action='new', id=amount)))
    t.add(types.InlineKeyboardButton(phrases.card, callback_data=vote_cb.new(action='card', id=amount)))
    # t.add(types.InlineKeyboardButton(phrases.exchange_rates, callback_data=vote_cb.new(action='rates', id=amount)))
    return t


async def delete_msg(chat_id, msg_id):
    try:
        await bot.delete_message(chat_id, msg_id)
    except:
        print("can't delete msg")


async def set_commands(dispatcher):
    commands = [
        types.BotCommand(command="/start", description="перезагрузить бота"),
        types.BotCommand(command="/help", description="справка"),
        # types.BotCommand(command="/rate", description="курс обмена"),
    ]
    await bot.set_my_commands(commands)


@dp.errors_handler(exception=MessageNotModified)  # for skipping this exception
async def message_not_modified_handler(update, error):
    return True


@dp.message_handler(commands='start', state='*')
async def cmd_start(message: types.Message,
                    state: FSMContext):
    await state.finish()
    await message.reply(phrases.welcome, reply_markup=get_keyboard(0), reply=False,
                        parse_mode='html'
                        )


@dp.message_handler(commands='help', state='*')
async def cmd_help(message: types.Message,
                   state: FSMContext):
    # TODO message send
    await state.finish()
    await message.reply(phrases.help, reply_markup=get_keyboard(0), reply=False,
                        parse_mode='html'
                        )


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# TODO reset state data when 'back' at amount/price
def create_buttons_lst(action, data=None) -> list:

    btns_lst = []

    locs = filter_data(action=action, country=data.get('country'), operation_type=data.get('operation_type'))

    for loc in locs:
        btn = types.InlineKeyboardButton(
            add_emoji(loc, action), callback_data=vote_cb.new(loc, action=action)
        )
        btns_lst.append(btn)
    return btns_lst


def create_menu(data=None, table_type=None, confirmation=False, btns_in_row=3, prev_action="exit", card_conf=False):
    btns = types.InlineKeyboardMarkup()
    if table_type:
        for couple in chunks(create_buttons_lst(table_type, data), btns_in_row):
            btns.row(*couple)

    if confirmation:
        btns.row(types.InlineKeyboardButton(
            phrases.yes, callback_data=vote_cb.new("no", action='conf')))
    if card_conf:
        btns.row(types.InlineKeyboardButton(
            phrases.yes, callback_data=vote_cb.new("no", action='card_conf')))

    btns.row(types.InlineKeyboardButton(
        phrases.back, callback_data=vote_cb.new(action=prev_action, id='0')))
    # btns.row(types.InlineKeyboardButton(
    #     phrases.cancel, callback_data=vote_cb.new("no", action='exit')))
    return btns


@dp.callback_query_handler(vote_cb.filter(action='rates'))
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    await Info.info.set()
    await state.update_data(query=query)
    await query.message.edit_text(phrases.rates_info, reply_markup=create_menu())


@dp.callback_query_handler(vote_cb.filter(action='card'), state='*')
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    async with state.proxy() as data:
        await Cards.bank.set()
        await state.update_data(query=query)
        # await query.message.edit_text(phrases.under_construction, reply_markup=create_menu())
        await query.message.edit_text(phrases.pick_bank,
                                      reply_markup=create_menu(table_type='card_bank', data=data, btns_in_row=1))


@dp.callback_query_handler(vote_cb.filter(action='new'), state='*')
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    async with state.proxy() as data:
        await Editing.country.set()
        await state.update_data(query=query)
        await query.message.edit_text(phrases.pick_country,
                                      reply_markup=create_menu(table_type='country', data=data, btns_in_row=2))


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
            reply_markup=create_menu(data=data, table_type='city', btns_in_row=2, prev_action='new'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.country.set()
        await Editing.next()


@dp.callback_query_handler(vote_cb.filter(action='city'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['city'] = callback_data['id']

            if data.get('country') not in ['Россия', 'Турция']:
                await query.message.edit_text(phrases.other_country,
                                              reply_markup=create_menu(confirmation=True))
                await Editing.confirmation.set()
                return

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_currency_to_sell, data=data),
            reply_markup=create_menu(data=data, table_type='currency_to_sell', prev_action='country'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.city.set()
        await Editing.next()


def get_operation_type(currency):
    if currency in db_dict.get('all_crypto'):
        return 'SELL'
    return 'BUY'


@dp.callback_query_handler(vote_cb.filter(action='currency_to_sell'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['currency_to_sell'] = callback_data['id']
        # else:
        #     await state.reset_state()

        data['operation_type'] = get_operation_type(data.get('currency_to_sell'))

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_currency_to_buy, data=data),
            reply_markup=create_menu(data=data, table_type='currency_to_buy', prev_action='city'))
        if callback_data and callback_data.get('id') == '0':
            data['price'] = None
            # data['amount'] = None
            await Editing.currency_to_sell.set()
        await Editing.next()
        # if callback_data and callback_data.get('id') == '0':
        #     await Editing.currency_to_sell.set()


@dp.callback_query_handler(vote_cb.filter(action='currency_to_buy'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['currency_to_buy'] = callback_data['id']

            operation_type = data.get('operation_type')
            data['price'] = calculate_price(data.get('country'), operation_type,
                                            data.get('currency_to_sell'), data.get('currency_to_buy'))
            if data['price'] <= 0:
                data['price'] = None
            # print(data['price'])

            # if operation_type == 'SELL':
            #     data['price'] = get_price(data.get('currency_to_sell'), data.get('currency_to_buy'), 'SELL')
            # elif operation_type == 'BUY':
            #     data['price'] = get_price(data.get('currency_to_buy'), data.get('currency_to_sell'), 'BUY')

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_amount, data=data),
            reply_markup=create_menu(prev_action='currency_to_sell'))

        if callback_data and callback_data.get('id') == '0':
            data['price'] = None
            # data['amount'] = None
            await Editing.currency_to_buy.set()
        await Editing.next()


@dp.message_handler(lambda message: not validate_amount(message.text), state=[Editing.amount, Cards.amount])
# @dp.callback_query_handler(vote_cb.filter(action='amount'), state='*')
async def process_amount_invalid(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        query = data.get('query')
        await delete_msg(message.chat.id, message.message_id)
        if await state.get_state() == 'Editing:amount':
            await query.message.edit_text(
                display_summary(phrase=phrases.err_amount, data=data),
                reply_markup=create_menu(prev_action='currency_to_buy'))
        else:
            await query.message.edit_text(
                card_summary(phrase=phrases.err_amount, data=data),
                reply_markup=create_menu(prev_action='card_currency_buy'))


@dp.message_handler(lambda message: validate_amount(message.text), state=Editing.amount)
# @dp.message_handler(state=Editing.amount)
@dp.callback_query_handler(vote_cb.filter(action='amount'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')

        # TODO probably useless
        cur_state = await state.get_state()
        # print(cur_state)
        if cur_state == 'Editing:amount':
            data['amount'] = float(message.text)
            # await state.update_data(amount=float(message.text))
            input_amount = float(message.text)

            if data.get('country') == 'Турция' and data.get('currency_to_sell') == 'USDT':
                if input_amount / 0.95238 < 5000:
                    data['price'] = 100 / 105  # 0.95238
                else:
                    data['price'] = 100 / 104  # 0.96154

            await delete_msg(message.chat.id, message.message_id)

        await query.message.edit_text(
            display_summary(phrase=phrases.pick_date, data=data),
            reply_markup=create_menu(data=data, table_type='date', prev_action='currency_to_buy'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.amount.set()
            # data['amount'] = None
        await Editing.next()


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
            reply_markup=create_menu(table_type='time', data=data, btns_in_row=1, prev_action='currency_to_buy'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.date.set()
        await Editing.next()


@dp.callback_query_handler(vote_cb.filter(action='time'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['time'] = callback_data['id']

        await query.message.edit_text(
            display_summary(data=data, phrase=phrases.ask),
            reply_markup=create_menu(confirmation=True, prev_action='date'))
        if callback_data and callback_data.get('id') == '0':
            await Editing.time.set()
        await Editing.next()


@dp.callback_query_handler(vote_cb.filter(action='conf'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):

    async with state.proxy() as data:

        query = data.get('query')

        if message.from_user.username == 'GeorgeKazakevich':
            print(message.from_user.id)
        await delete_msg(query.message.chat.id, query.message.message_id)

        await bot.send_message(query.from_user.id, phrases.success, parse_mode='html')
        await bot.send_message(query.from_user.id, display_summary(data), parse_mode='html')

        await bot.send_message(chat_id=settings.admin_id,
                               text=display_summary(data, username=message.from_user.username),
                               parse_mode='html')

        await bot.send_message(message.from_user.id, phrases.welcome, reply_markup=get_keyboard(0))

        if callback_data and callback_data.get('id') == '0':
            await Editing.confirmation.set()
        # await Editing.next()
        await state.finish()


@dp.callback_query_handler(vote_cb.filter(action='card_bank'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['bank'] = callback_data['id']

        await query.message.edit_text(
            card_summary(phrase=phrases.pick_currency_to_sell, data=data),
            reply_markup=create_menu(data=data, table_type='card_currency_sell', prev_action='card'))
        if callback_data and callback_data.get('id') == '0':
            await Cards.bank.set()
        await Cards.next()


@dp.callback_query_handler(vote_cb.filter(action='card_currency_sell'), state='*')
# @dp.callback_query_handler(vote_cb.filter(action='card_currency_sell'), state=Cards.currency_to_sell)
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['currency_to_sell'] = callback_data['id']
        # else:
        #     await state.reset_state()

        data['operation_type'] = get_operation_type(data.get('currency_to_sell'))

        await query.message.edit_text(
            card_summary(phrase=phrases.pick_currency_to_buy, data=data),
            reply_markup=create_menu(data=data, table_type='card_currency_buy', prev_action='card'))
        if callback_data and callback_data.get('id') == '0':
            data['price'] = None
            await Cards.currency_to_sell.set()
        await Cards.next()


@dp.callback_query_handler(vote_cb.filter(action='card_currency_buy'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data and callback_data.get('id') != '0':
            data['currency_to_buy'] = callback_data['id']

            operation_type = data.get('operation_type')
            data['price'] = calculate_price_card(operation_type, data.get('currency_to_sell'),
                                                 data.get('currency_to_buy'))
            if data['price'] <= 0:
                data['price'] = None

        # keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
        # btns_text = ('100', '200', '300', '400', '500', '600')
        # keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))
        # await query.message.reply('Amount?', reply_markup=keyboard_markup)
        await query.message.edit_text(
            card_summary(phrase=phrases.pick_amount, data=data),
            reply_markup=create_menu(prev_action='card_currency_sell'))

        if callback_data and callback_data.get('id') == '0':
            data['price'] = None
            await Cards.currency_to_buy.set()
        await Cards.next()


@dp.message_handler(state=Cards.amount)
@dp.callback_query_handler(vote_cb.filter(action='card_amount'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')

        cur_state = await state.get_state()
        if cur_state == 'Cards:amount':
            input_amount = message.text
            # await state.update_data(amount=float(message.text))
            data['amount'] = float(message.text)

            price = calculate_price_card(data.get('operation_type'), data.get('currency_to_sell'),
                                         data.get('currency_to_buy'), input_amount)
            if data.get('price') != price:
                data['price'] = price

            if data['price'] <= 0:
                data['price'] = None
            await delete_msg(message.chat.id, message.message_id)

        await query.message.edit_text(
            card_summary(data=data, phrase=phrases.ask),
            reply_markup=create_menu(card_conf=True, prev_action='card_currency_buy'))
        if callback_data and callback_data.get('id') == '0':
            await Cards.amount.set()
        await Cards.next()


@dp.callback_query_handler(vote_cb.filter(action='card_conf'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):

    async with state.proxy() as data:
        query = data.get('query')
        await delete_msg(query.message.chat.id, query.message.message_id)
        await bot.send_message(query.from_user.id, phrases.success, parse_mode='html')
        await bot.send_message(query.from_user.id, card_summary(data), parse_mode='html')
        for a_id in settings.admin_ids:
            await bot.send_message(chat_id=a_id,
                                   text=card_summary(data, username=message.from_user.username),
                                   parse_mode='html')
        await bot.send_message(message.from_user.id, phrases.welcome, reply_markup=get_keyboard(0))
        if callback_data and callback_data.get('id') == '0':
            await Cards.confirmation.set()
        await state.finish()


@dp.callback_query_handler(vote_cb.filter(action='exit'), state="*")
async def inline_kb_creating(query: types.CallbackQuery,
                             state: FSMContext,
                             callback_data: typing.Dict[str, str]):
    await state.finish()
    await query.message.edit_text(phrases.welcome, reply_markup=get_keyboard(0),
                                  parse_mode='html'
                                  )


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, on_startup=set_commands)  # skip_updates=True,
