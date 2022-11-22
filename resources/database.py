import sqlite3


class Database:

    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

    def add_user(self, user_id, first_name, username, referer_id):
        self.cursor.execute(f'INSERT INTO users (user_id, first_name, username, referer_id) VALUES ({user_id}, "{first_name}", "{username}", {referer_id})')
        self.conn.commit()

    def get_referal_pages(self, user_id):
        page_size = 20
        referals = self.cursor.execute(f'SELECT * FROM users WHERE referer_id={user_id}').fetchall()
        pages_data = []
        for i in range(0, len(referals), page_size):
            pages_data.append(referals[i:i + page_size])
        print(pages_data)

    def get_referals(self, user_id):
        return self.cursor.execute(f'SELECT * FROM users WHERE referer_id={user_id}').fetchall()

    def get_referer(self, user_id):
        return self.cursor.execute(f'SELECT referer_id FROM users WHERE user_id={user_id}').fetchone()[0]

    def get_user_firstname(self, user_id):
        return self.cursor.execute(f'SELECT first_name FROM users WHERE user_id={user_id}').fetchone()[0]

    def get_user_id(self, user_id):
        return self.cursor.execute(f'SELECT id FROM users WHERE user_id={user_id}').fetchone()[0]

    def get_user_by_id(self, id):
        return self.cursor.execute(f'SELECT * FROM users WHERE id={id}').fetchone()

    def get_user_by_user_id(self, user_id):
        return self.cursor.execute(f'SELECT * FROM users WHERE user_id={user_id}').fetchone()

    def user_exists(self, user_id):
        return bool(self.cursor.execute(f'SELECT id FROM users WHERE user_id={user_id}').fetchone())

    def user_exists_id(self, id):
        return bool(self.cursor.execute(f'SELECT user_id FROM users WHERE id={id}').fetchone())

    def user_is_worker(self, user_id):
        if self.cursor.execute(f'SELECT is_worker FROM users WHERE user_id={user_id}').fetchone()[0] == 2:
            return True
        return bool(self.cursor.execute(f'SELECT is_worker FROM users WHERE user_id={user_id}').fetchone()[0])

    def user_is_admin(self, user_id):
        return self.cursor.execute(f'SELECT is_worker FROM users WHERE user_id={user_id}').fetchone()[0]

    def get_user_balance(self, user_id):
        return self.cursor.execute(f'SELECT balance FROM users WHERE user_id={user_id}').fetchone()[0]

    def add_user_balance(self, id, sum):
        self.cursor.execute(f'UPDATE users SET balance=balance+{sum} WHERE id={id}')
        return self.conn.commit()

    def add_user_balance_user_id(self, user_id, sum):
        self.cursor.execute(f'UPDATE users SET balance=balance+{sum} WHERE user_id={user_id}')
        return self.conn.commit()

    def subtract_user_balance(self, user_id, sub):
        self.cursor.execute(f'UPDATE users SET balance=balance-{sub} WHERE user_id={user_id}')
        return self.conn.commit()

    def set_user_balance_user_id(self, user_id, sum):
        self.cursor.execute(f'UPDATE users SET balance={sum} WHERE user_id={user_id}')
        return self.conn.commit()

    def get_user_min_deposit(self, user_id):
        return self.cursor.execute(f'SELECT min_deposit FROM users WHERE user_id={user_id}').fetchone()[0]

    def set_user_min_deposit(self, user_id, sum):
        self.cursor.execute(f'UPDATE users SET min_deposit={sum} WHERE user_id={user_id}')
        return self.conn.commit()

    def get_user_win_status(self, user_id):
        return self.cursor.execute(f'SELECT win_status FROM users WHERE user_id={user_id}').fetchone()[0]

    def get_user_block_status(self, user_id):
        if not self.user_exists(user_id):
            return False
        return self.cursor.execute(f'SELECT bot_status FROM users WHERE user_id={user_id}').fetchone()[0]

    def set_user_block_status(self, user_id, status):
        self.cursor.execute(f'UPDATE users SET bot_status={status} WHERE user_id={user_id}')
        return self.conn.commit()

    def set_user_win_status(self, user_id, status):
        self.cursor.execute(f'UPDATE users SET win_status={status} WHERE user_id={user_id}')
        return self.conn.commit()

    def agree_confirmed(self, user_id):
        return bool(self.cursor.execute(f'SELECT agree_confirmed FROM users WHERE user_id={user_id}').fetchone())

    def agree_confirm(self, user_id):
        self.cursor.execute(f'UPDATE users SET agree_confirmed=True WHERE user_id={user_id}')

    def get_all_users(self):
        return self.cursor.execute('SELECT * FROM users').fetchall()

    def del_referer(self, user_id):
        self.cursor.execute(f'UPDATE users SET referer_id=0 WHERE user_id={user_id}')
        return self.conn.commit()

    def change_min_depos(self, user_id, min):
        self.cursor.execute(f'UPDATE users SET min_deposit={min} WHERE referer_id={user_id}')
        self.cursor.execute(f'UPDATE users SET min_deposit={min} WHERE user_id={user_id}')
        return self.conn.commit()

    def min_depos(self, user_id):
        return self.cursor.execute(f'SELECT min_deposit FROM users WHERE user_id={user_id}').fetchone()[0]

    def is_log(self, user_id):
        a = bool(self.cursor.execute(f'SELECT log_mamont FROM users WHERE user_id={user_id}').fetchone()[0])
        print(a)
        return a

    def get_all_mamonts(self):
        return self.cursor.execute(f'SELECT * FROM users WHERE is_worker=0').fetchall()

    def get_all_workers(self):
        return self.cursor.execute(f'SELECT * FROM users WHERE is_worker>0').fetchall()
