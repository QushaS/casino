

admin_id = 5443071551
bot_id = 'https://t.me/BetBoom_Online_Robot'

from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from resources.states import States

def butts(user_id):
    return InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('✅', callback_data=f'accept {str(user_id)}'),
                                                    InlineKeyboardButton('❌', callback_data=f'delete {str(user_id)}'))

bot = Bot('5709950094:AAHwWDeq7kXq4BjbUQjL1nv7zuKv40YuiQY', parse_mode='html')

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands='start', state='*')
async def hello_msg(msg: types.Message, state: FSMContext):
    await States.invited_from.set()
    await msg.answer(f'''<b>👋 Добро пожаловать, {msg.from_user.first_name}!</b>

<i>Перед вступлением в команду нужно ответить на пару вопросов:</i>

1. Откуда о нас узнали?''')

@dp.message_handler(state=States.invited_from)
async def exp_msg(msg: types.Message, state: FSMContext):
    await States.experience.set()
    await state.set_data({'from': msg.text})
    await msg.answer(f'2. Имеется ли у вас опыт работы в данной сфере? Если да, то какой?')

@dp.message_handler(state=States.experience)
async def time_msg(msg: types.Message, state: FSMContext):
    await States.time.set()
    await state.update_data({'exp': msg.text})
    await msg.answer(f'3. Сколько вы готовы уделять времени в день?')

@dp.message_handler(state=States.time)
async def info_msg(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    await States.long_state.set()
    await msg.answer('🕔 Успешно! Ожидайте одобрения заявки...')
    await bot.send_message(admin_id, f'<b>📄 Новая заявка!</b>\n\n<i>Где узнал о нас: {data["from"]}\nОпыт работы: {data["exp"]}\nГотов уделять: {msg.text}</i>',
                           reply_markup=butts(msg.from_user.id))

@dp.callback_query_handler(text_startswith='accept', state='*')
async def accept_man(call: types.CallbackQuery):
    await call.message.edit_text(call.message.text + f'\n\n✅ Заявка <b><a href="tg://user?id={call.data.split()[1]}">{call.data.split()[1]}</a></b> одобрена')
    await bot.send_message(call.data.split()[1], f'<b>✅ Вы были успешно приняты в команду, добро пожаловать!</b>',
                           reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('Бот для работы', url=f'{bot_id}?start=worker'),
                                                                              InlineKeyboardButton('Мануалы', url='https://t.me/+e29hFzwKm3ZiYjk1'),
                                                                              InlineKeyboardButton('Чат', url='https://t.me/+Iob-GAG2TJEzYTg9'),
                                                                              InlineKeyboardButton('Выплаты', url='https://t.me/+VdPIgTKDbthkMDc1', ),
                                                                              InlineKeyboardButton('Информация', url='https://t.me/+H0888kO2QYo4Y2Q1')
                                                                              ))

@dp.callback_query_handler(text_startswith='delete', state='*')
async def del_man(call: types.CallbackQuery):
    await call.message.edit_text(f'❌ Заявка под айди {call.data.split()[1]} отклонена!')

print('''
██╗███╗░░██╗██╗░░░██╗██╗████████╗███████╗██████╗░
██║████╗░██║██║░░░██║██║╚══██╔══╝██╔════╝██╔══██╗
██║██╔██╗██║╚██╗░██╔╝██║░░░██║░░░█████╗░░██████╔╝
██║██║╚████║░╚████╔╝░██║░░░██║░░░██╔══╝░░██╔══██╗
██║██║░╚███║░░╚██╔╝░░██║░░░██║░░░███████╗██║░░██║
╚═╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝''')

executor.start_polling(dp)
