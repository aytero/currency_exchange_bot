import asyncio
import logging

import typing
from aiogram import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified
from db.model import *
from db.session import *

from core.config import settings

from core.validation import validate_charset, validate_name, name_in_names

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
    t.add(types.InlineKeyboardButton('Choose options for cash',    callback_data=vote_cb.new(action='new', id=amount)))
    t.add(types.InlineKeyboardButton('Show exchange rates', callback_data=vote_cb.new(action='rates', id=amount)))
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


class Editing(StatesGroup):
    country = State()
    city = State()
    currency = State()
    time_slot = State()
    amount = State()
    confirmation = State()


class Info(StatesGroup):
    info = State()


rates_info = (
    '- Exchange rates -\n'
    '- <b>RUB-USDT</b> – 0.012 usdt\n'
    '- <b>USDT-RUB</b> – 80.87 rub\n'
)


@dp.callback_query_handler(vote_cb.filter(action='rates'))  # , state=State.in_account)
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    await Info.info.set()
    await state.update_data(query=query)  # bot_id=callback_data.get('id'),
    await query.message.edit_text(rates_info, reply_markup=create_menu())


pick_country = 'Выберите страну'


@dp.callback_query_handler(vote_cb.filter(action='new'))  # , state=State.in_account)
async def inline_kb_creating(
        query: types.CallbackQuery,
        state: FSMContext,
        callback_data: typing.Dict[str, str]):
    async with state.proxy() as data:
        await Editing.country.set()
        await state.update_data(query=query)  # bot_id=callback_data.get('id'),
        await query.message.edit_text(pick_country, reply_markup=create_menu(Countries))


COUNTRY, CITY, CURRENCY = range(3)


def create_bottons_lst(table_type, country=None, search=False, rename=False) -> list:

    action = {
        Cities: "city",
        Countries: "country",
        Currencies: "currency",
        Slots: "time_slot",
        Amount: "amount",
        # User: "conf",
    }[table_type]

    # if rename:
    #     action = "e_" + action
    # elif search:
    #     action = "s_" + action

    btns_lst = []
    locs = session.query(table_type)
    if 'city' in action:
        # logger.info("city in action")
        locs = locs.join(Countries).filter(Countries.name == country)
    for loc in locs.all():
        btn = types.InlineKeyboardButton(
            loc.name, callback_data=vote_cb.new(loc.name, action=action)
        )
        btns_lst.append(btn)

    return btns_lst


def create_menu(table_type=None, country=None, search=False, rename=False,
                admin=False):
    btns = types.InlineKeyboardMarkup()
    if table_type:
        for couple in chunks(create_bottons_lst(
                table_type, country=country, search=search, rename=rename), 3):
            btns.row(*couple)
    if rename:  # TODO change var name also TODO delete unconfirmed records
        btns.row(types.InlineKeyboardButton(
            "Yes", callback_data=vote_cb.new("no", action='conf')))
    btns.row(types.InlineKeyboardButton(
            "Back", callback_data=vote_cb.new("no", action='exit')
        ))
    return btns


pick_city = 'Выберите город'
# err_input = f'Неверный ввод, попробуйте еще раз'
pick_currency = f'Выберите валютную пару'
pick_time = f'Выберите время:'
pick_amount = f'Provide amount you want to exchange (sell):'
confirmation_text = f'Confirm action:'
# request_text = f'Provide date and time'
# err_city = f'Incorrect input, enter again'


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
            pick_city, reply_markup=create_menu(Cities, country=data['country']))
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

        await query.message.edit_text(
            pick_currency, reply_markup=create_menu(Currencies, country=data['country']))
        await Editing.next()


@dp.message_handler(state=Editing.currency)
@dp.callback_query_handler(vote_cb.filter(action='currency'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data:
            data['currency'] = callback_data['id']

        await query.message.edit_text(
            pick_time, reply_markup=create_menu(Slots, country=data['country']))
        await Editing.next()


@dp.message_handler(state=Editing.time_slot)
@dp.callback_query_handler(vote_cb.filter(action='time_slot'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')
        if callback_data:
            data['slot'] = callback_data['id']

        await query.message.edit_text(
            pick_amount, reply_markup=create_menu(country=data['country']))
        await Editing.next()


def display_summary(user: User):
    msg = f'Here is your appointment summary: \n'
    msg += f"<b>Страна</b>: {user.slot.currency.city.country.name}\n"
    msg += f"<b>Город</b>: {user.slot.currency.city.name}\n"
    msg += f"<b>Валютая пара</b>: {user.slot.currency.name}\n"
    msg += f"<b>Сумма</b>: {user.amount.name}\n"
    msg += f"<b>Дата и время</b>: {user.slot.name}\n"
    msg += f'\n<b>Do you confirm your appointment?</b> \n'
    return msg


@dp.message_handler(state=Editing.amount)
@dp.callback_query_handler(vote_cb.filter(action='amount'), state='*')
async def new_entry_account_manager(message: types.Message,
                                    state: FSMContext,
                                    callback_data: typing.Dict[str, str] = None):
    async with state.proxy() as data:
        query = data.get('query')

        input_amount = message.text
        data['amount'] = input_amount
        # print(input_amount + "inpttt")

        country = session.query(Countries).filter(Countries.name == data['country']).first()
        await delete_msg(message.chat.id, message.message_id)

        if not country:
            country = Countries(name=data['country'])
            session.add(country)

        city = (session.query(Cities).
                join(Countries, Countries.id == country.id).
                filter(Cities.name == data['city']).first())
        if not city:
            city = Cities(name=data['city'])
            session.add(city)

        country.cities.append(city)

        currency = (session.query(Currencies).
                    join(Cities, Cities.id == city.id).
                    filter(Currencies.name == data['currency']).first())
        # if not currency:
        #     currency = Currencies(name=data['currency'])
        #     session.add(currency)
        city.currencies.append(currency)

        slot = session.query(Slots).join(Currencies, Currencies.id == currency.id).filter(
            Slots.name == data['slot']).first()
        # if not slot:
        #     slot = Slot(name=data['slot'])
        #     session.add(slot)
        currency.slots.append(slot)

        amount = session.query(Amount).filter(Amount.name == data['amount']).first()
        if not amount:
            amount = Amount(name=data['amount'])
            session.add(amount)

        user = User(tname=message.from_user.username,
                    tid=message.from_user.id,
                    slot=slot,
                    amount=amount)

        session.add(user)
        session.commit()

        await query.message.edit_text(
            display_summary(user), reply_markup=create_menu(rename=True))

        await Editing.next()


@dp.message_handler(state=Editing.confirmation)
@dp.callback_query_handler(vote_cb.filter(action='conf'), state='*')
async def new_entry_account_manager(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
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
    n = session.query(User).filter(User.id == callback_data['id']).first()
    if n:
        session.delete(n)
        session.commit()
    await delete_msg(query.message.chat.id, query.message.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, on_startup=set_commands)  # skip_updates=True,
