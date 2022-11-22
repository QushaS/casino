from aiogram.dispatcher.filters.state import State, StatesGroup

class States(StatesGroup):
    select_money_to_play_state = State()
    qiwi_set_payment_state = State()
    money_set_payment_state = State()
    send_mamont_message_state = State()
    withdraw_state = State()
    min_depos_state = State()
    mamont_spam_state = State()
    worker_spam_state = State()
    write_balance_state = State()
    write_mamont_id_state = State()
    write_mamont_id_state1 = State()
    write_worker_id_state = State()

    invited_from = State()
    experience = State()
    time = State()
    long_state = State()
