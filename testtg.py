import telebot
import random
import sqlite3
import time
import threading

API_TOKEN = 'YOUR_API_TOKEN'
ADMIN_ID = [6321157988]
OWNER_ID = [797141384]
VOLUNTEER_ID = []
DIRECTOR_ID = []

bot = telebot.TeleBot(API_TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('bot_database.txt', check_same_thread=False)
cursor = conn.cursor()

# Таблицы
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
    user_id INTEGER PRIMARY KEY
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS volunteers (
    user_id INTEGER PRIMARY KEY
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS directors (
    user_id INTEGER PRIMARY KEY
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS bans (
    user_id INTEGER PRIMARY KEY,
    end_time INTEGER,
    reason TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS warns (
    user_id INTEGER,
    reason TEXT,
    timestamp INTEGER
)
''')

conn.commit()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 
                 """Используйте следующие команды:
                 /report (юзерID) (причина) - Подать жалобу
                 /acceptreport (номер) (ранг) - Принять жалобу
                 /addadm (юзерID) - Добавить админа
                 /addvolunteer (юзерID) - Добавить волонтёра
                 /adddirector (юзерID) - Добавить директора
                 /check (юзерID) - Проверить репутацию
                 /checkmy - Проверить свой статус
                 /ban (юзерID) (время) (причина) - Забанить пользователя
                 /warn (юзерID) (причина) - Выдать выговор
                 /mute (юзерID) (причина) - Замутить пользователя
                 /addgarant (юзерID) - Сделать гарантом
                 /delbase (юзерID) (причина) - Удалить из базы""")

# Existing functions and handlers...

@bot.message_handler(commands=['addvolunteer'])
def cmd_add_volunteer(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для добавления в волонтёры.')
        return

    volunteer_id = get_user_id(args[0])
    if volunteer_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    add_volunteer(volunteer_id)
    bot.reply_to(message, f'Пользователь {volunteer_id} добавлен как волонтёр.')

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

    add_director(director_id)
    bot.reply_to(message, f'Пользователь {director_id} добавлен как директор.')

@bot.message_handler(commands=['ban'])
def cmd_ban(message):
    if message.from_user.id not in get_admins() and message.from_user.id not in DIRECTOR_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 3:
        bot.reply_to(message, 'Используйте: /ban (юзерID) (время в минутах) (причина)')
        return

    user_id = get_user_id(args[0])
    if user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    try:
        time_ban = int(args[1]) * 60  # Convert minutes to seconds
    except ValueError:
        bot.reply_to(message, 'Некорректное время бана.')
        return

    reason = ' '.join(args[2:])
    end_time = int(time.time()) + time_ban
    add_ban(user_id, end_time, reason)

    bot.reply_to(message, f'Пользователь {user_id} забанен на {args[1]} минут. Причина: {reason}')
    threading.Thread(target=remove_ban_after_time, args=(user_id,)).start()

@bot.message_handler(commands=['warn'])
def cmd_warn(message):
    if message.from_user.id not in get_admins() and message.from_user.id not in DIRECTOR_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Используйте: /warn (юзерID) (причина)')
        return

    user_id = get_user_id(args[0])
    if user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    reason = ' '.join(args[1:])
    add_warn(user_id, reason)

    bot.reply_to(message, f'Пользователю {user_id} выдан выговор. Причина: {reason}')

@bot.message_handler(commands=['mute'])
def cmd_mute(message):
    if message.from_user.id not in get_admins() and message.from_user.id not in DIRECTOR_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Используйте: /mute (юзерID) (причина)')
        return

    user_id = get_user_id(args[0])
    if user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    reason = ' '.join(args[1:])
    add_mute(user_id, reason)

    bot.reply_to(message, f'Пользователь {user_id} замучен. Причина: {reason}')

def add_volunteer(user_id):
    cursor.execute('INSERT OR IGNORE INTO volunteers (user_id) VALUES (?)', (user_id,))
    conn.commit()

def add_director(user_id):
    cursor.execute('INSERT OR IGNORE INTO directors (user_id) VALUES (?)', (user_id,))
    conn.commit()

def add_ban(user_id, end_time, reason):
    cursor.execute('INSERT OR REPLACE INTO bans (user_id, end_time, reason) VALUES (?, ?, ?)', (user_id, end_time, reason))
    conn.commit()

def remove_ban_after_time(user_id):
    time.sleep(60)  # Wait the ban duration
    cursor.execute('DELETE FROM bans WHERE user_id = ?', (user_id,))
    conn.commit()

def add_warn(user_id, reason):
    timestamp = int(time.time())
    cursor.execute('INSERT INTO warns (user_id, reason, timestamp) VALUES (?, ?, ?)', (user_id, reason, timestamp))
    conn.commit()

def add_mute(user_id, reason):
    cursor.execute('INSERT INTO bans (user_id, end_time, reason) VALUES (?, ?, ?)', (user_id, int(time.time()) + 300, reason))  # Mute for 5 minutes
    conn.commit()

def get_user_ban(user_id):
    cursor.execute('SELECT end_time, reason FROM bans WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def get_user_warns(user_id):
    cursor.execute('SELECT reason, timestamp FROM warns WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

def get_admins():
    cursor.execute('SELECT user_id FROM admins')
    return {row[0] for row in cursor.fetchall()}

def check_user_rank(user_id):
    ban_info = get_user_ban(user_id)
    if ban_info:
        return 'Забанен до ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ban_info[0]))
    
    if user_id in get_scammers():
        return 'скамер'
    elif user_id in get_guarantees():
        return 'гарант'
    elif user_id in get_volunteers():
        return 'волонтёр'
    elif user_id in get_directors():
        return 'директор'
    return 'Нету в базе'

def get_volunteers():
    cursor.execute('SELECT user_id FROM volunteers')
    return {row[0] for row in cursor.fetchall()}

def get_directors():
    cursor.execute('SELECT user_id FROM directors')
    return {row[0] for row in cursor.fetchall()}

# Existing functions...

# Запуск бота с обработкой исключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
