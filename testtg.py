import telebot
import random
import sqlite3
import time
import threading

API_TOKEN = '7994365938:AAGHSzJZ1Vp8Hl8SKNeIecfre3wLMvnTR3s'
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

cursor.execute('''
CREATE TABLE IF NOT EXISTS mutes (
    user_id INTEGER PRIMARY KEY,
    end_time INTEGER,
    reason TEXT
)
''')

conn.commit()

# Existing function...

@bot.message_handler(commands=['unmute'])
def cmd_unmute(message):
    if message.from_user.id not in get_admins() and message.from_user.id not in DIRECTOR_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для снятия мута.')
        return

    user_id = get_user_id(args[0])
    if user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    cursor.execute('DELETE FROM mutes WHERE user_id = ?', (user_id,))
    conn.commit()
    
    bot.reply_to(message, f'Пользователь {user_id} размучен.')

@bot.message_handler(commands=['unban'])
def cmd_unban(message):
    if message.from_user.id not in get_admins() and message.from_user.id not in DIRECTOR_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для снятия бана.')
        return

    user_id = get_user_id(args[0])
    if user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    cursor.execute('DELETE FROM bans WHERE user_id = ?', (user_id,))
    conn.commit()

    bot.reply_to(message, f'Пользователь {user_id} разбанен.')

@bot.message_handler(commands=['delmute'])
def cmd_delmute(message):
    if message.from_user.id not in get_admins() and message.from_user.id not in DIRECTOR_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, 'Используйте: /delmute (юзерID) (причина) (время в минутах)')
        return

    user_id = get_user_id(args[1])
    if user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    reason = args[2]
    mute_time = int(args[3]) * 60  # Convert minutes to seconds
    end_time = int(time.time()) + mute_time

    add_mute(user_id, reason)
    bot.reply_to(message, f'Пользователь {user_id} замучен. Причина: {reason}')

    # Удаление последних 5 сообщений пользователя (логика может варьироваться)
    # Assuming you have a chat_id to delete messages from
    # chat_id should be predetermined or passed
    delete_last_messages(chat_id, user_id, 5)

def delete_last_messages(chat_id, user_id, count):
    # Логика удаления последних `count` сообщений от `user_id`
    # Это может быть реализовано разными способами, так как API Telegram не поддерживает
    # удаление сообщений по ID, если у вас нет их ID заранее. Данную реализацию
    # нужно подстраивать под ваши требования.
    pass

def remove_ban_after_time(user_id):
    time.sleep(60)  # Wait the ban duration
    cursor.execute('DELETE FROM bans WHERE user_id = ?', (user_id,))
    conn.commit()

def add_mute(user_id, reason):
    cursor.execute('INSERT OR REPLACE INTO mutes (user_id, end_time, reason) VALUES (?, ?, ?)',
                   (user_id, int(time.time()) + 300, reason))  # Mute for 5 minutes
    conn.commit()

def get_user_mute(user_id):
    cursor.execute('SELECT end_time, reason FROM mutes WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def get_user_id(arg):
    # Здесь вам нужно реализовать логику, чтобы получить user_id по аргументу
    # Это основано на том, что user_id может быть в формате ID или @username
    pass

# Existing functions...

# Запуск бота с обработкой исключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
