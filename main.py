import logging
import config
import aiohttp_socks
from aiogram import Bot, Dispatcher, executor, types

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)


bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

main_dict = {
    'cus': {
        'text': 'Меню заказчика',
        'b_text': 'Я заказчик',
        'cr_ord': {
            'text': 'Опишите Ваше задание в двух словах',
            'b_text': u'\U0001F4DD Создать задание'
        },
        'my_ord': {
            'text': 'Список заданий',
            'b_text': u'\U0001F4D6 Мои задания'
        },
        'bal': {
            'text': 'Меню баланса',
            'b_text': u'\U0001F4B0 Баланс:'
        },
        'set': {
            'text': 'Меню настроек',
            'b_text': u'\U00002699 Настройки',
            'to_wor': {
                'text': 'Меню настроек',
                'b_text': 'Я фрилансер'
            }
        }
    },
    'wor': {
        'text': 'Меню фрилансера',
        'b_text': 'Я фрилансер',
        'my_ord': {
            'text': 'Ваши задания',
            'b_text': u'\U0001F5D2 Мои задания'
        },
        'geo_find': {
            'text': 'Геопоиск',
            'b_text': u'\U0001F30D Геопоиск'
        },
        'cats': {
            'text': 'Список категорий',
            'b_text': u'\U0001F5C3 Найти категории'
        },
        'set': {
            'text': 'Меню настроек',
            'b_text': u'\U0001F6E0 Настройки',
            'to_cus': {
                'text': 'Меню настроек',
                'b_text': 'Я заказчик'
            }
        },
    },
    'bal': {
        'text': 'Меню баланса',
        'b_text': u'\U0001F4B0 Баланс:'
    },
    'about': {
        'b_text': u'\U0001F4CD О сервисе',
        'text': 'Содержание о сервисе',
        'back': {
            'b_text': 'Назад'
        }
    }
}


class Ticket(StatesGroup):
    wf_body = State()
    wf_price = State()


def cus_menu():
    cus_dict = main_dict['cus']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row_width = 1
    markup.add(types.KeyboardButton(cus_dict['cr_ord']['b_text']))
    markup.row_width = 2
    markup.add(types.KeyboardButton(cus_dict['my_ord']['b_text']),
               types.KeyboardButton(main_dict['bal']['b_text']))
    markup.add(types.KeyboardButton(main_dict['about']['b_text']),
               types.KeyboardButton(cus_dict['set']['b_text']))
    return markup


def cus_set_menu():
    cur_dict = main_dict['cus']['set']
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton('To worker', callback_data='wor')]
        ]
    )


def wor_menu():
    wor_dict = main_dict['wor']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row_width = 2
    markup.add(types.KeyboardButton(wor_dict['my_ord']['b_text']),
               types.KeyboardButton(wor_dict['cats']['b_text']))
    markup.add(types.KeyboardButton(wor_dict['geo_find']['b_text']),
               types.KeyboardButton(main_dict['bal']['b_text']))
    markup.add(types.KeyboardButton(main_dict['about']['b_text']),
               types.KeyboardButton(wor_dict['set']['b_text']))
    return markup


def wor_set_menu():
    cur_dict = main_dict['wor']['set']
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton('To customer', callback_data='cus')]
        ]
    )


@dp.message_handler(commands=['start'])
async def starter(msg: types.Message):
    await bot.send_message(chat_id=msg.from_user.id, text="Главное меню", reply_markup=cus_menu())


async def ticket_1(msg: types.Message):
    await msg.answer("Введите основную информацию", reply_markup=types.ReplyKeyboardRemove())
    await Ticket.wf_body.set()


@dp.message_handler(state=Ticket.wf_body, content_types=types.ContentTypes.TEXT)
async def ticket_2(msg: types.Message, state: FSMContext):
    await state.update_data(body=msg.text.lower())
    await Ticket.next()
    await msg.answer("Введите предложение по цене")


@dp.message_handler(state=Ticket.wf_price, content_types=types.ContentTypes.TEXT)
async def ticket_3(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await msg.answer(f"Задание: {user_data['body']}.\nПредложение: {msg.text} рублей.")
    await state.finish()


@dp.message_handler()
async def worker(msg: types.Message):
    if msg.text[0] == '📝':
        await ticket_1(msg)
    elif msg.text[0] == '📖':
        await msg.answer('📖 Мои задания')  # cus
        return
    elif msg.text[0] == '⚙':
        await msg.answer('⚙ Настройки', reply_markup=cus_set_menu())
        return
    elif msg.text[0] == '🗒':
        await msg.answer('🗒 Мои задания')  # wor
        return
    elif msg.text[0] == '🗃':
        await msg.answer('🗃 Категории')
        return
    elif msg.text[0] == '🌍':
        await msg.answer('🌍 Геопоиск')
        return
    elif msg.text[0] == '🛠':
        await msg.answer('🛠 Настройки', reply_markup=wor_set_menu())
        return
    elif msg.text[0] == '📍':
        await msg.answer('📍 О сервисе')  # common
        return
    elif msg.text[0] == '💰':
        await msg.answer('💰 Баланс')
        return


@dp.callback_query_handler(lambda call: True)
async def main_handler(call: types.CallbackQuery):
    print(call)
    data = call.data
    user_id = call.from_user.id

    if data in ['cr_ord']:
        return

    if data == 'cus':
        await bot.send_message(chat_id=user_id, text='Customer', reply_markup=cus_menu())
    elif data == 'wor':
        await bot.send_message(chat_id=user_id, text='Worker', reply_markup=wor_menu())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
