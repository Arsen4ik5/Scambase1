import telebot
import sqlite3
import random
import time

API_TOKEN = '7275319279:AAGZh_GzI4iO5Vsb3lcBsF0RLUq5Meh-yh8'
ADMIN_ID = []
OWNER_ID = [6321157988, 797141384]
VOLUNTEER_ID = []
DIRECTOR_ID = []
GARANT_ID = []
PROGRAMIST_ID = [6321157988]  # Начальный программирующий пользователь
slito_skammerov = 0  
zayavki = 0

bot = telebot.TeleBot(API_TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('angel_database.txt', check_same_thread=False)
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
CREATE TABLE IF NOT EXISTS verified_guarantees (
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

cursor.execute('''
CREATE TABLE IF NOT EXISTS zayavki (
    user_id INTEGER,
    count INTEGER,
    PRIMARY KEY (user_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS slito_skammerov (
    user_id INTEGER,
    count INTEGER,
    PRIMARY KEY (user_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS checks (
    user_id INTEGER,
    check_count INTEGER,
    PRIMARY KEY (user_id)
)
''')

conn.commit()

# Статусы пользователей
mute_status = {}
banned_users = {}
warn_count = {}
check_count = {}

reports = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 
                 """ Вас приветствует бот базы  Greenlight Base
                 """)

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

# Получение ранга пользователя
def check_user_rank(user_id):
    if user_exists(user_id, 'admins'):
        return 'Администратор'
    elif user_exists(user_id, 'guarantees'):
        return 'Гарант'
    elif user_exists(user_id, 'verified_guarantees'):
        return 'Проверен гарантом'
    elif user_exists(user_id, 'volunteer'):
        return 'Волонтёр'
    elif user_exists(user_id, 'director'):
        return 'Директор'
    elif user_exists(user_id, 'scammers'):
        return 'Скаммер'
    elif user_exists(user_id, 'slito_skammerov'):
        return 'Возможный скаммер'
    elif user_id in OWNER_ID:
        return 'Владелец'
    elif user_id in PROGRAMIST_ID:
        return None  # Не отображать ранг программиста
    return 'Нету в базе'

# Получение информации о скаммере
def get_scammers_info(user_id):
    cursor.execute('SELECT evidence, reason FROM scammers WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    return row if row else (None, None)

# Получение количества слитых скаммеров
def get_slitoskammerov(user_id):
    cursor.execute('SELECT count FROM slito_skammerov WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

# Получение списка гарантированных пользователей
def get_guarantees():
    cursor.execute('SELECT user_id FROM guarantees')
    return [row[0] for row in cursor.fetchall()]

# Получение списка проверенных гарантов
def get_verified_guarantees():
    cursor.execute('SELECT user_id FROM verified_guarantees')
    return [row[0] for row in cursor.fetchall()]

# Получение списка волонтёров
def get_volunteers():
    cursor.execute('SELECT user_id FROM volunteer')
    return [row[0] for row in cursor.fetchall()]

# Проверка, есть ли пользователь в базе
def check_if_in_database(user_id):
    if user_exists(user_id, 'admins') or user_exists(user_id, 'guarantees') or user_exists(user_id, 'verified_guarantees') or user_exists(user_id, 'volunteer') or user_exists(user_id, 'director') or user_exists(user_id, 'scammers'):
        return True
    return False

# Добавление скаммера в базу
def add_to_scammers(user_id, evidence, reason):
    cursor.execute('INSERT INTO scammers (user_id, evidence, reason) VALUES (?, ?, ?)', (user_id, evidence, reason))
    conn.commit()

# Удаление пользователя из базы
def remove_user(user_id):
    cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM guarantees WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM verified_guarantees WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM scammers WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM volunteer WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM director WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM zayavki WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM slito_skammerov WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM checks WHERE user_id = ?', (user_id,))
    conn.commit()

# Удаление траста от пользователя
def remove_from_guarantees(user_id):
    cursor.execute('DELETE FROM guarantees WHERE user_id = ?', (user_id,))
    conn.commit()

# Удаление пользователя из списка проверенных гарантов
def remove_from_verified_guarantees(user_id):
    cursor.execute('DELETE FROM verified_guarantees WHERE user_id = ?', (user_id,))
    conn.commit()

# Добавление пользователя в гарантии
def add_to_guarantees(user_id):
    cursor.execute('INSERT INTO guarantees (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Добавление пользователя как проверенного гаранта
def add_verified_guarantee(user_id):
    cursor.execute('INSERT INTO verified_guarantees (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Добавление администратора
def add_admin(user_id):
    cursor.execute('INSERT INTO admins (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Добавление волонтёра
def add_volunteer(user_id):
    cursor.execute('INSERT INTO volunteer (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Добавление директора
def add_director(user_id):
    cursor.execute('INSERT INTO director (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Команда для мута
@bot.message_handler(commands=['mute'])
def mute(message):
    if message.from_user.id in ADMIN_ID or message.from_user.id in OWNER_ID or message.from_user.id in DIRECTOR_ID:
        try:
            user_id = int(message.text.split()[1])
            reason = message.text.split()[2]
            duration = message.text.split()[3]
            duration_in_seconds = 0
            
            if duration.endswith('m'):
                duration_in_seconds = int(duration[:-1]) * 60
            elif duration.endswith('h'):
                duration_in_seconds = int(duration[:-1]) * 3600
            elif duration.endswith('y'):
                duration_in_seconds = int(duration[:-1]) * 31536000  # 1 год = 31536000 секунд
            else:
                duration_in_seconds = int(duration)

            mute_status[user_id] = (time.time() + duration_in_seconds)
            bot.reply_to(message, f"На {user_id} были наложены чары мута")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /mute <user_id> <reason> <duration(m/h/y)>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для размута
@bot.message_handler(commands=['unmute'])
def unmute(message):
    if message.from_user.id in ADMIN_ID or message.from_user.id in OWNER_ID or message.from_user.id in DIRECTOR_ID:
        try:
            user_id = int(message.text.split()[1])
            if user_id in mute_status:
                del mute_status[user_id]
                bot.reply_to(message, f"С {user_id} были сняты чары мута.")
            else:
                bot.reply_to(message, f"Пользователь {user_id} не замучен.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /unmute <user_id>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для бана
@bot.message_handler(commands=['ban'])
def ban(message):
    if message.from_user.id in ADMIN_ID or message.from_user.id in OWNER_ID or message.from_user.id in DIRECTOR_ID:
        try:
            user_id = int(message.text.split()[1])
            reason = message.text.split()[2]
            duration = message.text.split()[3]
            duration_in_seconds = 0
            
            if duration.endswith('m'):
                duration_in_seconds = int(duration[:-1]) * 60
            elif duration.endswith('h'):
                duration_in_seconds = int(duration[:-1]) * 3600
            elif duration.endswith('y'):
                duration_in_seconds = int(duration[:-1]) * 31536000  # 1 год = 31536000 секунд
            else:
                duration_in_seconds = int(duration)

            banned_users[user_id] = (time.time() + duration_in_seconds)
            bot.reply_to(message, f"На {user_id} были наложены чары бана по причине: '{reason}' ")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /ban <user_id> <reason> <duration(m/h/y)>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для разбанивания
@bot.message_handler(commands=['unban'])
def unban(message):
    if message.from_user.id in ADMIN_ID or message.from_user.id in OWNER_ID or message.from_user.id in DIRECTOR_ID:
        try:
            user_id = int(message.text.split()[1])
            if user_id in banned_users:
                del banned_users[user_id]
                bot.reply_to(message, f"С {user_id} были сняты чары бана.")
            else:
                bot.reply_to(message, f"Пользователь {user_id} не забанен.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /unban <user_id>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для варна
@bot.message_handler(commands=['warn'])
def warn(message):
    if message.from_user.id in ADMIN_ID or message.from_user.id in OWNER_ID or message.from_user.id in DIRECTOR_ID:
        try:
            user_id = int(message.text.split()[1])
            warn_count[user_id] = warn_count.get(user_id, 0) + 1
            bot.reply_to(message, f"Человеку {user_id} был выдан варн. Всего варнов: {warn_count[user_id]}")
            
            # Проверка на три варна
            if warn_count[user_id] >= 3:
                ban_duration = 31536000  # Например, 1 год
                banned_users[user_id] = (time.time() + ban_duration)
                bot.reply_to(message, f"На {user_id} были наложены чары бана на 1 год за 3 варна.")
                del warn_count[user_id]  # Сбросить счетчик варнов
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /warn <user_id>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для кика
@bot.message_handler(commands=['kick'])
def kick(message):
    if message.from_user.id in ADMIN_ID or message.from_user.id in OWNER_ID or message.from_user.id in DIRECTOR_ID:
        try:
            user_id = int(message.text.split()[1])
            bot.kick_chat_member(message.chat.id, user_id)
            bot.reply_to(message, f"Пользователь {user_id} был кикнут из чата.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /kick <user_id>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для проверки репутации пользователя
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

    rank = check_user_rank(check_user_id)
    slitoskammerov = get_slitoskammerov(check_user_id)
    iskalivbase = check_if_in_database(check_user_id)

    # Увеличение счетчика обращений к базе
    check_count[check_user_id] = check_count.get(check_user_id, 0) + 1

    if check_user_id in get_guarantees():
        bot.send_photo(message.chat.id, 'https://imageup.ru/img205/4967023/1000012384.jpg', caption=f"""
Вывод информации о пользователе:
🆔 Id: {check_user_id}
🔁 Репутация: Гарант
Шанс скама: 0%
🚮 Слито Скамеров: {slitoskammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
        return

    if check_user_id in get_verified_guarantees():
        bot.send_photo(message.chat.id, 'https://imageup.ru/img205/4967023/1000012384.jpg', caption=f"""
Вывод информации о пользователе:
🆔 Id: {check_user_id}
🔁 Репутация: Проверен гарантом
Шанс скама: 0%
🚮 Слито Скамеров: {slitoskammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
        return

    if check_user_id in get_volunteers():
        bot.send_photo(message.chat.id, 'https://imageup.ru/img205/4967023/1000012384.jpg', caption=f"""
Вывод информации о пользователе:
🆔 Id: {check_user_id}
🔁 Репутация: Волонтёр
Шанс скама: 0%
🚮 Слито Скамеров: {slitoskammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
        return

    if rank == 'Скаммер':
        evidence, reason = get_scammers_info(check_user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img298/4967024/1000012382.jpg', caption=f"""
Вывод информации о пользователе:
🆔 Id: {check_user_id}
🔁 Репутация: {rank}
❗ Шанс скама: 99%
📝 Доказательства: {evidence}
📋 Причина: {reason}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank == 'Возможный скаммер':
        evidence, reason = get_scammers_info(check_user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img92/4967025/1000012385.jpg', caption=f"""
Вывод информации о пользователе:
🆔 Id: {check_user_id}
🔁 Репутация: {rank}
❗ Шанс скама: 70%
📝 Доказательства: {evidence}
📋 Причина: {reason}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank == 'Владелец':
        bot.send_photo(message.chat.id, 'https://imageup.ru/img31/4967021/1000012386.jpg', caption=f"""
Вывод информации о пользователе:
🆔 Id: {check_user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zayavki}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank in ['Администратор', 'Директор']:
        bot.send_photo(message.chat.id, 'https://imageup.ru/img31/4967021/1000012386.jpg', caption=f"""
Вывод информации о пользователе:
🆔 Id: {check_user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zayavki}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    else:
        bot.send_photo(message.chat.id, 'https://imageup.ru/img1/4967020/1000012383.jpg', caption=f"""
Вывод информации о пользователе:
Нету в базе:
🆔 Id: {check_user_id}
🔁 Репутация: Нету в базе
❓ Шанс скама: 50%
🚮 Слито Скамеров: {slitoskammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")

# Команда для проверки своего статуса
@bot.message_handler(commands=['checkmy'])
def cmd_check_my_status(message):
    user_id = message.from_user.id
    
    if user_id in get_guarantees():
        slitoskammerov = get_slitoskammerov(user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img205/4967023/1000012384.jpg', caption=f"""
Вывод информации о вас:
🆔 Id: {user_id}
🔁 Репутация: Гарант
Шанс скама: 0%
🚮 Слито Скамеров: {slitoskammerov}
🔍 Искали в базе: {check_if_in_database(user_id)}
✅ Greenlight Base
""")
        return

    if user_id in get_verified_guarantees():
        slitoskammerov = get_slitoskammerov(user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img205/4967023/1000012384.jpg', caption=f"""
Вывод информации о вас:
🆔 Id: {user_id}
🔁 Репутация: Проверен гарантом
Шанс скама: 0%
🚮 Слито Скамеров: {slitoskammerov}
🔍 Искали в базе: {check_if_in_database(user_id)}
✅ Greenlight Base
""")
        return

    if user_id in get_volunteers():
        slitoskammerov = get_slitoskammerov(user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img205/4967023/1000012384.jpg', caption=f"""
Вывод информации о вас:
🆔 Id: {user_id}
🔁 Репутация: Волонтёр
Шанс скама: 0%
🚮 Слито Скамеров: {slitoskammerov}
🔍 Искали в базе: {check_if_in_database(user_id)}
✅ Greenlight Base
""")
        return

    rank = check_user_rank(user_id)
    slitoskammerov = get_slitoskammerov(user_id)
    iskalivbase = check_if_in_database(user_id)

    # Увеличение счетчика обращений к базе
    check_count[user_id] = check_count.get(user_id, 0) + 1

    if rank == 'Владелец':
        bot.send_photo(message.chat.id, 'https://imageup.ru/img31/4967021/1000012386.jpg', caption=f"""
Вывод информации о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zayavki}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank in ['Администратор', 'Директор']:
        bot.send_photo(message.chat.id, 'https://imageup.ru/img154/4967022/1000012388.jpg', caption=f"""
Вывод информации о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 10%
🚮 Заявки: {zayavki}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank == 'Скаммер':
        evidence, reason = get_scammers_info(user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img298/4967024/1000012382.jpg', caption=f"""
Вывод информации о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
❗ Шанс скама: 99%
📝 Доказательства: {evidence}
📋 Причина: {reason}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank == 'Возможный скаммер':
        evidence, reason = get_scammers_info(user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img92/4967025/1000012385.jpg', caption=f"""
Вывод информации о вас:
🆔 Id: {user_id}
🔁 Репутация: {rank}
❗ Шанс скама: 70%
📝 Доказательства: {evidence}
📋 Причина: {reason}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    else:
        bot.send_photo(message.chat.id, 'https://imageup.ru/img1/4967020/1000012383.jpg', caption=f"""
Вывод информации о вас:
Нету в базе:
🆔 Id: {user_id}
🔁 Репутация: Нету в базе
❓ Шанс скама: 50%
🚮 Слито Скамеров: {slitoskammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")

# Команда для назначения статуса "Проверен гарантом"
@bot.message_handler(commands=['trust'])
def trust_user(message):
    if message.from_user.id in ADMIN_ID or message.from_user.id in OWNER_ID or message.from_user.id in DIRECTOR_ID or message.from_user.id in GARANT_ID:
        try:
            user_id = get_user_id(message.text.split()[1])
            if user_id:
                add_verified_guarantee(user_id)
                bot.reply_to(message, f"Пользователю {user_id} был выдан статус 'Проверен гарантом'.")
            else:
                bot.reply_to(message, "Некорректный ID или username.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /trust <user_id>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для снятия статуса "Проверен гарантом"
@bot.message_handler(commands=['untrust'])
def untrust_user(message):
    if message.from_user.id in ADMIN_ID or message.from_user.id in OWNER_ID or message.from_user.id in DIRECTOR_ID or message.from_user.id in GARANT_ID:
        try:
            user_id = get_user_id(message.text.split()[1])
            if user_id:
                remove_from_verified_guarantees(user_id)
                bot.reply_to(message, f"У пользователя {user_id} был снят статус 'Проверен гарантом'.")
            else:
                bot.reply_to(message, "Некорректный ID или username.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /untrust <user_id>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для назначения ранга
@bot.message_handler(commands=['rank'])
def assign_rank(message):
    if message.from_user.id in OWNER_ID :
        try:
            user_id = int(message.text.split()[1])
            rank = message.text.split()[2]
            if rank in ['Администратор', 'Гарант', 'Проверен гарантом', 'Волонтёр', 'Директор', 'Programist']:
                remove_user(user_id)  # Удаляем пользователя из всех таблиц
                if rank == 'Администратор':
                    add_admin(user_id)
                elif rank == 'Гарант':
                    add_to_guarantees(user_id)
                elif rank == 'Проверен гарантом':
                    add_verified_guarantee(user_id)
                elif rank == 'Волонтёр':
                    add_volunteer(user_id)
                elif rank == 'Директор':
                    add_director(user_id)
                elif rank == 'Programist':
                    bot.reply_to(message, "извините у данного пользователя не существующий ранг ")
                bot.reply_to(message, f"Пользователю {user_id} был выдан ранг '{rank}'.")
            else:
                bot.reply_to(message, "Некорректный ранг.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте: /rank <user_id> <ранг>")
    else:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")

# Команда для увеличения количества слитых скаммеров
@bot.message_handler(commands=['spasibo'])
def increase_slito_skammerov(message):
    if len(message.text.split()) == 2:
        user_id = int(message.text.split()[1])
        current_count = get_slitoskammerov(user_id)
        cursor.execute('INSERT OR REPLACE INTO slito_skammerov (user_id, count) VALUES (?, ?)', (user_id, current_count + 1))
        conn.commit()
        bot.reply_to(message, f"Количество слитых скаммеров для {user_id} увеличено на 1.")
    else:
        bot.reply_to(message, "Используйте: /spasibo <user_id>")

# Команда для добавления заявок
@bot.message_handler(commands=['z'])
def add_zayavki(message):
    if len(message.text.split()) == 3:
        user_id = int(message.text.split()[1])
        count = int(message.text.split()[2])
        cursor.execute('INSERT OR REPLACE INTO zayavki (user_id, count) VALUES (?, COALESCE((SELECT count FROM zayavki WHERE user_id = ?), 0) + ?)', (user_id, user_id, count))
        conn.commit()
        bot.reply_to(message, f"Заявки для {user_id} увеличены на {count}.")
    else:
        bot.reply_to(message, "Используйте: /z <user_id> <количество>")

# Команда для удаления из базы
@bot.message_handler(commands=['noscam'])
def remove_scam(message):
    if len(message.text.split()) == 3:
        user_id = int(message.text.split()[1])
        reason = message.text.split()[2]
        remove_user(user_id)
        bot.reply_to(message, f"Пользователь {user_id} был удален из базы по причине: {reason}.")
    else:
        bot.reply_to(message, "Используйте: /noscam <user_id> <причина>")

# Команда для добавления пользователя в базу скаммеров
@bot.message_handler(commands=['scam'])
def add_scam(message):
    if len(message.text.split()) == 6:
        username = message.text.split()[1]
        reputation = message.text.split()[2]
        evidence = message.text.split()[3]
        reason = message.text.split()[4]
        cursor.execute('INSERT INTO scammers (user_id, evidence, reason) VALUES (?, ?, ?)', (username, evidence, reason))  # username может быть ID
        conn.commit()
        bot.reply_to(message, f"Пользователь {username} добавлен в базу скаммеров с репутацией '{reputation}'.")
    else:
        bot.reply_to(message, "Используйте: /scam <юзернейм> <репутация> <доказательства> <причина>")

# Проверка состояний пользователей
@bot.message_handler(func=lambda message: True)
def check_user_status(message):
    user_id = message.from_user.id

    # Проверка мута
    if user_id in mute_status:
        if time.time() < mute_status[user_id]:
            bot.delete_message(message.chat.id, message.message_id)
            return
        else:
            del mute_status[user_id]

    # Проверка бана
    if user_id in banned_users:
        if time.time() < banned_users[user_id]:
            bot.kick_chat_member(message.chat.id, user_id)
            return
        else:
            del banned_users[user_id]

# Запуск бота с обработкой исключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
