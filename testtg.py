import telebot
import sqlite3

API_TOKEN = '7994365938:AAGHSzJZ1Vp8Hl8SKNeIecfre3wLMvnTR3s'
ADMIN_ID = []
OWNER_ID = [6321157988, 797141384]
VOLUNTEER_ID = []
DIRECTOR_ID = []

bot = telebot.TeleBot(API_TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
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
                 /revoke_trust (юзернейм) - Забрать траст у пользователя
                 /addvolunteer (юзерID) - Добавить волонтера
                 /adddirector (юзерID) - Добавить директора
                 /ban (юзерID) (время) (причина) - Забанить пользователя
                 /unban (юзерID) - Разбанить пользователя
                 /mute (юзерID) (причина) - Замутить пользователя
                 /unmute (юзерID) - Убрать мут
                 /warn (юзерID) (причина) - Выдать варн
                 /delmute (юзерID) (причина) (время) - Замутить и удалить последние 5 сообщений нарушителя
                 """)

# Получение Id пользователя
def get_user_id(param):
    try:
        if param.isdigit():
            return int(param)
        else:
            user = bot.get_chat(param)
            return user.id if user else None
    except Exception:
        return None

# Определение прав доступа для команд
def user_has_permission(message, role_list):
    return message.from_user.id in role_list

# Проверка существования пользователя в таблице
def user_exists(user_id, table):
    cursor.execute(f'SELECT user_id FROM {table} WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is not None

# Команда /checkmy
@bot.message_handler(commands=['checkmy'])
def cmd_check_my_status(message):
    user_id = message.from_user.id
    rank = check_user_rank(user_id)

    bot.reply_to(message, 
                  f"🔎Результат поиска:\n"
                  f"🔥Репутация: {rank}\n"
                  f"🆔Айди: {user_id}\n")

# Добавление роли волонтера
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

# Добавление роли директора
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

# Команда /ban
@bot.message_handler(commands=['ban'])
def cmd_ban(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 3:
        bot.reply_to(message, 'Используйте: /ban (юзерID) (время) (причина)')
        return

    user_to_ban = get_user_id(args[0])
    ban_time = args[1]  # например, '30' для 30 минут
    reason = ' '.join(args[2:])

    if user_to_ban is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    add_ban(user_to_ban, ban_time, reason)
    bot.reply_to(message, f'Пользователь {user_to_ban} забанен на {ban_time} минут(ы). Причина: {reason}')

# Команда /unban
@bot.message_handler(commands=['unban'])
def cmd_unban(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return
    
    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Используйте: /unban (юзерID)')
        return

    user_to_unban = get_user_id(args[0])
    
    if user_to_unban is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    remove_ban(user_to_unban)
    bot.reply_to(message, f'Пользователь {user_to_unban} был разблокирован.')

# Команда /mute
@bot.message_handler(commands=['mute'])
def cmd_mute(message):
    if not user_has_permission(message, VOLUNTEER_ID + DIRECTOR_ID + ADMIN_ID):
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Используйте: /mute (юзерID) (причина)')
        return

    user_to_mute = get_user_id(args[0])
    reason = ' '.join(args[1:])

    if user_to_mute is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    add_mute(user_to_mute, reason)
    bot.reply_to(message, f'Пользователь {user_to_mute} замучен. Причина: {reason}')

# Команда /unmute
@bot.message_handler(commands=['unmute'])
def cmd_unmute(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Используйте: /unmute (юзерID)')
        return

    user_to_unmute = get_user_id(args[0])

    if user_to_unmute is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    remove_mute(user_to_unmute)
    bot.reply_to(message, f'Пользователь {user_to_unmute} был размучен.')

# Команда /warn
@bot.message_handler(commands=['warn'])
def cmd_warn(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Используйте: /warn (юзерID) (причина)')
        return

    user_to_warn = get_user_id(args[0])
    reason = ' '.join(args[1:])

    if user_to_warn is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    # Здесь можно добавить логику для выдачи предупреждений

    bot.reply_to(message, f'Варн выдан для пользователя {user_to_warn}. Причина: {reason}')

# Команда /delmute
@bot.message_handler(commands=['delmute'])
def cmd_delmute(message):
    if message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 3:
        bot.reply_to(message, 'Используйте: /delmute (юзерID) (причина) (время)')
        return

    user_to_mute = get_user_id(args[0])
    reason = args[1]
    time_duration = args[2]  # duration can be processed if needed

    if user_to_mute is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    add_mute(user_to_mute, reason)
    bot.reply_to(message, f'Пользователь {user_to_mute} замучен и удалены последние 5 сообщений. Причина: {reason}')

# Добавление пользователя в волонтеры
def add_volunteer(user_id):
    cursor.execute('INSERT OR IGNORE INTO volunteer (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Добавление пользователя в директоры
def add_director(user_id):
    cursor.execute('INSERT OR IGNORE INTO director (user_id) VALUES (?)', (user_id,))
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

# Запуск бота с обработкой исключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
