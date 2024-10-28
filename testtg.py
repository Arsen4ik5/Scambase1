import telebot
import sqlite3
import random

API_TOKEN = '7994365938:AAGHSzJZ1Vp8Hl8SKNeIecfre3wLMvnTR3s'  # Замените на свой токен
ADMIN_ID = [6321157988]
OWNER_ID = [797141384]
VOLUNTEER_ID = []
DIRECTOR_ID = []
GARANT_ID = []

bot = telebot.TeleBot(API_TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('angeless_database.txt', check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц в базе данных
cursor.execute('''
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS guarantees (
    user_id INTEGER PRIMARY KEY
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS scammers (
    user_id INTEGER PRIMARY KEY,
    evidence TEXT,
    reason TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS volunteer (
    user_id INTEGER PRIMARY KEY
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS director (
    user_id INTEGER PRIMARY KEY
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS bans (
    user_id INTEGER,
    time INTEGER,
    reason TEXT,
    PRIMARY KEY (user_id, time)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS mutes (
    user_id INTEGER,
    reason TEXT,
    time INTEGER,
    PRIMARY KEY (user_id, time)
)
''')

conn.commit()

reports = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 
                 """Используйте следующие команды:
                 /report (юзерID) (причина) - Подать жалобу
                 /acceptreport (номер) (ранг) - Принять жалобу
                 /addadm (юзерID) - Добавить админа
                 /check (юзерID) - Проверить репутацию
                 /checkmy - Проверить свой статус
                 /addgarant (юзерID) - Сделать гарантом
                 /delbase (юзерID) (причина) - Удалить из базы
                 /scam (юзернейм) (доказательства) (причина) - Добавить пользователя в скам базу
                 /trust (юзернейм) - Выдать траст пользователю
                 /revoke_trust (юзернейм) - Забрать траст у пользователя""")

# Получение ID
def get_user_id(param):
    try:
        if param.isdigit():
            return int(param)
        else:
            user = bot.get_chat(param)
            return user.id if user else None
    except Exception:
        return None

# Проверка существования пользователя в таблице
def user_exists(user_id, table):
    cursor.execute(f'SELECT user_id FROM {table} WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is not None

@bot.message_handler(commands=['report'])
def cmd_report(message):
    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, "Используйте: /report (юзерID) (причина)")
        return

    reported_user_id = get_user_id(args[0])
    if reported_user_id is None:
        bot.reply_to(message, "Некорректный ID или username.")
        return

    reason = ' '.join(args[1:])
    report_id = random.randint(10000, 99999)
    reports[report_id] = {'user_id': reported_user_id, 'status': 'pending', 'reason': reason, 'rank': None}
    bot.reply_to(message, f'Ваша жалоба подана. Номер жалобы: {report_id}')

@bot.message_handler(commands=['acceptreport'])
def cmd_accept_report(message):
    if message.from_user.id not in get_admins():
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Укажите номер жалобы и ранг (скамер, гарант).')
        return

    try:
        report_id = int(args[0])
        rank = args[1].lower()
    except ValueError:
        bot.reply_to(message, 'Некорректный ввод. Убедитесь, что номер жалобы — это число.')
        return

    if report_id in reports:
        reports[report_id]['status'] = 'accepted'
        reports[report_id]['rank'] = rank

        if rank == 'скамер':
            add_to_scammers(reports[report_id]['user_id'], "доказательства на скам", reports[report_id]['reason'])
        elif rank == 'гарант':
            add_to_guarantees(reports[report_id]['user_id'])

        bot.reply_to(message, f'Жалоба {report_id} принята. Ранг установлен: {rank}.')
    else:
        bot.reply_to(message, 'Такой жалобы не существует.')

@bot.message_handler(commands=['addvolunteer'])
def cmd_add_volunteer(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для добавления в волонтеры.')
        return

    volunteer_id = get_user_id(args[0])
    if volunteer_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    if user_exists(volunteer_id, 'volunteer'):
        bot.reply_to(message, f'Пользователь {volunteer_id} уже является волонтером.')
        return

    add_volunteer(volunteer_id)
    bot.reply_to(message, f'Пользователь {volunteer_id} добавлен как волонтер.')

@bot.message_handler(commands=['addadm'])
def cmd_add_admin(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для добавления в администраторы.')
        return

    new_admin = get_user_id(args[0])
    if new_admin is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    add_admin(new_admin)
    bot.reply_to(message, f'Пользователь {new_admin} добавлен как администратор.')

@bot.message_handler(commands=['check'])
def cmd_check(message):
    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для проверки.')
        return
    
    check_user_id = get_user_id(args[0])
    if check_user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    if check_user_id in get_guarantees():
        bot.reply_to(message, 
                      f"🔎Результат поиска:\n"
                      f"🔥Репутация: Проверен гарантом\n"
                      f"🆔Айди: {check_user_id}\n")
        return

    rank = check_user_rank(check_user_id)
    
    if rank == 'скамер':
        evidence, reason = get_scammers_info(check_user_id)
        bot.reply_to(message, 
                      f"🔎Результат поиска:\n"
                      f"🔥Репутация: {rank}\n"
                      f"🆔Айди: {check_user_id}\n"
                      f"📝Доказательства: {evidence}\n"
                      f"📋Причина: {reason}\n")
    elif rank == 'гарант':
        bot.reply_to(message, 
                      f"🔎Результат поиска:\n"
                      f"🔥Репутация: {rank}\n"
                      f"🆔Айди: {check_user_id}\n")
    elif rank in ['админ', 'директор']:
        bot.reply_to(message, 
                      f"🔎Результат поиска:\n"
                      f"🔥Репутация: {rank}\n"
                      f"🆔Айди: {check_user_id}\n")
    else:
        bot.reply_to(message, 
                      f"🔎Результат поиска:\n"
                      f"🔥Репутация: {rank}\n"
                      f"🆔Айди: {check_user_id}\n")

@bot.message_handler(commands=['scam'])
def cmd_scam(message):
    if message.from_user.id not in ADMIN_ID and message.from_user.id not in OWNER_ID and message.from_user.id not in VOLUNTEER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        bot.reply_to(message, 'Используйте: /scam (юзернейм) (доказательства) (причина)')
        return

    username = args[1]
    evidence = args[2]
    reason = args[3]

    scam_user_id = get_user_id(username)
    if scam_user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    add_to_scammers(scam_user_id, evidence, reason)
    
    bot.reply_to(message, f'Пользователь {username} (ID: {scam_user_id}) был добавлен в базу скамеров.\nДоказательства: {evidence}\nПричина: {reason}')

@bot.message_handler(commands=['checkmy'])
def cmd_check_my_status(message):
    user_id = message.from_user.id
    
    if user_id in get_guarantees():
        bot.reply_to(message, 
                      f"🔎Результат поиска:\n"
                      f"🔥Репутация: Проверен гарантом\n"
                      f"🆔Айди: {user_id}\n")
        return

    rank = check_user_rank(user_id)

    bot.reply_to(message, 
                  f"🔎Результат поиска:\n"
                  f"🔥Репутация: {rank}\n"
                  f"🆔Айди: {user_id}\n")

@bot.message_handler(commands=['addgarant'])
def cmd_add_garant(message):
    if message.from_user.id not in ADMIN_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для добавления в гарант.')
        return

    garant_id = get_user_id(args[0])
    if garant_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    add_to_guarantees(garant_id)
    bot.reply_to(message, f'Пользователь {garant_id} добавлен как гарант.')

@bot.message_handler(commands=['delbase'])
def cmd_del_base(message):
    if message.from_user.id not in ADMIN_ID and message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Используйте: /delbase (юзерID) (причина)')
        return

    del_user_id = get_user_id(args[0])
    if del_user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    remove_user(del_user_id)
    bot.reply_to(message, f'Пользователь {del_user_id} удален из базы. Причина: {" ".join(args[1:])}.')

@bot.message_handler(commands=['trust'])
def cmd_trust(message):
    if message.from_user.id not in OWNER_ID and message.from_user.id not in GARANT_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Используйте: /trust (юзернейм)')
        return

    username = args[0]
    trust_user_id = get_user_id(username)
    if trust_user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    if trust_user_id in get_scammers():
        bot.reply_to(message, 'Нельзя выдать траст скамеру.')
        return

    if trust_user_id not in get_guarantees():
        add_to_guarantees(trust_user_id)
        bot.reply_to(message, f'Пользователю {username} (ID: {trust_user_id}) выдан траст.')
    else:
        bot.reply_to(message, f'Пользователь {username} уже является гарантированным.')

@bot.message_handler(commands=['adddirector'])
def cmd_add_director(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для добавления в директора.')
        return

    director_id = get_user_id(args[0])
    if director_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    if user_exists(director_id, 'director'):
        bot.reply_to(message, f'Пользователь {director_id} уже является директором.')
        return

    add_director(director_id)
    bot.reply_to(message, f'Пользователь {director_id} добавлен как директор.')

@bot.message_handler(commands=['deldirector'])
def cmd_del_director(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для удаления из директоров.')
        return

    director_id = get_user_id(args[0])
    if director_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    if not user_exists(director_id, 'director'):
        bot.reply_to(message, f'Пользователь {director_id} не является директором.')
        return

    remove_director(director_id)
    bot.reply_to(message, f'Пользователь {director_id} удален из директоров.')

@bot.message_handler(commands=['deladmin'])
def cmd_del_admin(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для удаления из администраторов.')
        return

    admin_id = get_user_id(args[0])
    if admin_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    if not user_exists(admin_id, 'admins'):
        bot.reply_to(message, f'Пользователь {admin_id} не является администратором.')
        return

    remove_admin(admin_id)
    bot.reply_to(message, f'Пользователь {admin_id} удален из администраторов.')

@bot.message_handler(commands=['ban'])
def kick_user(message):
    if message.from_user.id not in OWNER_ID and message.from_user.id not in DIRECTOR_ID and message.from_user.id not in ADMIN_ID:
        bot.reply_to(message, "[❌] Ошибка")
        return

    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(
                message, 
                f"Пользователь {message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(
            message,
            "Эта команда должна быть использована в ответ "
            "на сообщение пользователя, которого вы хотите забанить.")

@bot.message_handler(commands=['untrust'])
def cmd_revoke_trust(message):
    if message.from_user.id not in GARANT_ID and message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Используйте: /revoke_trust (юзернейм)')
        return

    username = args[0]
    revoke_user_id = get_user_id(username)
    if revoke_user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    if revoke_user_id not in get_guarantees():
        bot.reply_to(message, 'У данного пользователя нет траста.')
        return

    remove_from_guarantees(revoke_user_id)
    bot.reply_to(message, f'Траст у пользователя {username} (ID: {revoke_user_id}) забран.')

# Добавление пользователя в волонтёры
def add_volunteer(user_id):
    cursor.execute('INSERT OR IGNORE INTO volunteer (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Удаление пользователя из волонтёров
def remove_volunteer(user_id):
    cursor.execute('DELETE FROM volunteer WHERE user_id = ?', (user_id,))
    conn.commit()

# Добавление пользователя в директоры
def add_director(user_id):
    cursor.execute('INSERT OR IGNORE INTO director (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Удаление пользователя из директоров
def remove_director(user_id):
    cursor.execute('DELETE FROM director WHERE user_id = ?', (user_id,))
    conn.commit()

# Команды для добавления в бан
def add_ban(user_id, time, reason):
    cursor.execute('INSERT OR REPLACE INTO bans (user_id, time, reason) VALUES (?, ?, ?)', (user_id, time, reason))
    conn.commit()

# Убираем бан
def remove_ban(user_id):
    cursor.execute('DELETE FROM bans WHERE user_id = ?', (user_id,))
    conn.commit()

def add_mute(user_id, reason):
    cursor.execute('INSERT OR REPLACE INTO mutes (user_id, reason, time) VALUES (?, ?, ?)', (user_id, reason, 5))  # Time can be configured
    conn.commit()

def remove_mute(user_id):
    cursor.execute('DELETE FROM mutes WHERE user_id = ?', (user_id,))
    conn.commit()

def add_admin(user_id):
    cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (user_id,))
    conn.commit()

def remove_admin(user_id):
    cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
    conn.commit()

def check_user_rank(user_id):
    if user_id in get_scammers():
        return 'скамер'
    elif user_id in get_guarantees():
        return 'гарант'
    elif user_id in get_admins():
        return 'админ'
    elif user_id in get_volunteers():
        return 'волонтёр'
    elif user_id in get_directors():
        return 'директор'
    return 'Нету в базе'

def get_guarantees():
    cursor.execute('SELECT user_id FROM guarantees')
    return {row[0] for row in cursor.fetchall()}

def get_scammers():
    cursor.execute('SELECT user_id FROM scammers')
    return {row[0] for row in cursor.fetchall()}

def get_volunteers():
    cursor.execute('SELECT user_id FROM volunteer')
    return {row[0] for row in cursor.fetchall()}

def get_directors():
    cursor.execute('SELECT user_id FROM director')
    return {row[0] for row in cursor.fetchall()}

def get_admins():
    cursor.execute('SELECT user_id FROM admins')
    return {row[0] for row in cursor.fetchall()}

def add_to_guarantees(user_id):
    cursor.execute('INSERT OR IGNORE INTO guarantees (user_id) VALUES (?)', (user_id,))
    conn.commit()

def remove_from_guarantees(user_id):
    cursor.execute('DELETE FROM guarantees WHERE user_id = ?', (user_id,))
    conn.commit()

def add_to_scammers(user_id, evidence, reason):
    cursor.execute('INSERT OR IGNORE INTO scammers (user_id, evidence, reason) VALUES (?, ?, ?)', (user_id, evidence, reason))
    conn.commit()

def remove_user(user_id):
    # Удаление из всех таблиц, если требуется
    remove_volunteer(user_id)
    remove_admin(user_id)
    remove_director(user_id)
    remove_from_guarantees(user_id)
    cursor.execute('DELETE FROM scammers WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM bans WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM mutes WHERE user_id = ?', (user_id,))
    conn.commit()

# Запуск бота с обработкой исключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
