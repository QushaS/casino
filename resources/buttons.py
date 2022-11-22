from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from resources.database import Database

db = Database('database.db')

agree_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('✅ Принять', callback_data='accept_agreements'))


def main_kb(worker):
    main_kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(KeyboardButton('Играть 🎰'),
                                                                         KeyboardButton('Профиль 💠'))

    main_kb_work = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(KeyboardButton('Играть 🎰'),
                                                                              KeyboardButton('Профиль 💠'),
                                                                              KeyboardButton('Меню воркера 🛠'))
    main_kb_work_admin = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    main_kb_work_admin.add(KeyboardButton('Играть 🎰'),
                            KeyboardButton('Профиль 💠'),
                            KeyboardButton('Меню воркера 🛠'))
    main_kb_work_admin.row(KeyboardButton('Админ панель 🔱'))
    if worker == 1:
        return main_kb_work
    elif worker == 2:
        return main_kb_work_admin
    else:
        return main_kb

def adm_kb(status):
    if status == 2:
        admin_kb = InlineKeyboardMarkup(row_width=1)

profile_kb = InlineKeyboardMarkup(row_width=1)
profile_kb.row(InlineKeyboardButton('Пополнить 📥', callback_data='deposit'),
               InlineKeyboardButton('Вывести 📤', callback_data='withdraw'))

profile_kb.add(  # InlineKeyboardButton('Наш официальный сайт ✅', url='betboom.ru')
    InlineKeyboardButton('Тех.поддержка 👨‍💻', url='https://t.me/official_betboom'))

game_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('Играть 🎰', callback_data='play'))

admin_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton('💬 Рассылка', callback_data='spam_menu'),
    InlineKeyboardButton('💸 Выдача баланса', callback_data='give_balance_to'),
    InlineKeyboardButton('🦣 Передать мамонта', callback_data='give_mamont_to'),
    InlineKeyboardButton('🥝 Qiwi меню', callback_data='qiwi_menu')
)

spam_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton('✉ Мамонтам', callback_data='spam_mamonts'),
    InlineKeyboardButton('💌 Воркерам', callback_data='spam_workers')
)

def game_select_kb(money):
    game_process_kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton('< 50', callback_data=f'lower {money}'),
        InlineKeyboardButton('> 50', callback_data=f'upper {money}'),
        InlineKeyboardButton('= 50', callback_data=f'equal {money}'))
    return game_process_kb


def worker_kb(status):
    if status > 0:
        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(InlineKeyboardButton('Найти мамонта 🔎', switch_inline_query_current_chat='m='))
        kb.add(InlineKeyboardButton('Топ воркеров 🏆', callback_data='top'),
               InlineKeyboardButton('Информация ℹ', callback_data='info'))
        kb.row(InlineKeyboardButton('Указать мин. депозит 💸', callback_data='min_depos'))
        return kb


def mamont_set_kb(mamont_id, one_or_not=''):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(InlineKeyboardButton('Изменить баланс 💸', callback_data=f'change_balance{one_or_not} {mamont_id}'),
           InlineKeyboardButton('Изменить статус 📩', callback_data=f'change_status {mamont_id}'))
    kb.add(InlineKeyboardButton('Обновить 🔃', callback_data=f'update {mamont_id}'),
           InlineKeyboardButton('Вкл / Выкл логирование 👁', callback_data=f'en_log {mamont_id}'),
           InlineKeyboardButton('Отправить сообщение 🖊', callback_data=f'send_msg {mamont_id}'),
           InlineKeyboardButton('Удалить мамонта 🗑', callback_data=f'del_mamont {mamont_id}'))

    return kb

def mamont_set_state_kb(mamont_id):
    stateboard = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Всегда выигрыш', callback_data=f'set_state 0 {mamont_id}'),
                                                       InlineKeyboardButton('Верификация', callback_data=f'set_state 3 {mamont_id}'),
                                                       InlineKeyboardButton('Всегда проигрыш', callback_data=f'set_state 2 {mamont_id}'),
                                                       InlineKeyboardButton('Налог', callback_data=f'set_state 4 {mamont_id}'),
                                                       InlineKeyboardButton('Рандом', callback_data=f'set_state 1 {mamont_id}'),
                                                       InlineKeyboardButton('Аккаунт заблокирован', callback_data=f'set_state 5 {mamont_id}'))

    return stateboard

def mamont_withdrawal(mamont_id, mon):
    print(mamont_id)
    keyboard = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('✅ Вывести', callback_data=f'withdrawal 1 {mamont_id} {mon}'),
                                                     InlineKeyboardButton('❌ Отказ', callback_data=f'withdrawal 0 {mamont_id}'))

    return keyboard
