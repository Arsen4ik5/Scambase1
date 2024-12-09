import telebot
import sqlite3
import random

API_TOKEN = '7275319279:AAGZh_GzI4iO5Vsb3lcBsF0RLUq5Meh-yh8'
ADMIN_ID = []
OWNER_ID = [6321157988, 797141384]
VOLUNTEER_ID = []
DIRECTOR_ID = []
GARANT_ID = []
SLITOscam = 0
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
CREATE TABLE IF NOT EXISTS slito_scam (
    user_id INTEGER,
    count INTEGER,
    PRIMARY KEY (user_id)
)
''')

conn.commit()

reports = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 
                 """Используйте следующие команды:
                 /check (юзерID) - Проверить репутацию
                 /checkmy - Проверить свой статус
                 /noscam (юзерID) (причина) - Удалить из базы
                 /scam (юзернейм) (доказательства) (причина/возможный скам) - Добавить пользователя в скам базу
                 /trust (юзернейм) - Выдать траст пользователю
                 /rank (юзерID) (ранг) - Установить ранг пользователю""")

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
    elif user_exists(user_id, 'volunteer'):
        return 'Волонтёр'
    elif user_exists(user_id, 'director'):
        return 'Директор'
    elif user_exists(user_id, 'scammers'):
        return 'Скаммер'
    elif user_exists(user_id, 'slito_scam'):
        return 'Возможный скаммер'
    elif user_id in OWNER_ID:
        return 'Владелец'
    return 'Нету в базе'

# Получение информации о скаммере
def get_scammers_info(user_id):
    cursor.execute('SELECT evidence, reason FROM scammers WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    return row if row else (None, None)

# Получение количества слитых скаммеров
def get_slitoscammerov(user_id):
    cursor.execute('SELECT count FROM slito_scam WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

# Проверка, есть ли пользователь в базе
def check_if_in_database(user_id):
    if user_exists(user_id, 'admins') or user_exists(user_id, 'guarantees') or user_exists(user_id, 'volunteer') or user_exists(user_id, 'director') or user_exists(user_id, 'scammers'):
        return True
    return False

# Добавление скаммера в базу
def add_to_scammers(user_id, evidence, reason, rank):
    cursor.execute('INSERT INTO scammers (user_id, evidence, reason) VALUES (?, ?, ?)', (user_id, evidence, reason))
    conn.commit()

# Удаление пользователя из базы
def remove_user(user_id):
    cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM guarantees WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM scammers WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM volunteer WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM director WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM zayavki WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM slito_scam WHERE user_id = ?', (user_id,))
    conn.commit()

# Удаление траста от пользователя
def remove_from_guarantees(user_id):
    cursor.execute('DELETE FROM guarantees WHERE user_id = ?', (user_id,))
    conn.commit()

# Добавление пользователя в гарантии
def add_to_guarantees(user_id):
    cursor.execute('INSERT INTO guarantees (user_id) VALUES (?)', (user_id,))
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
    
    slitoscammerov = get_slitoscammerov(check_user_id)
    iskalivbase = check_if_in_database(check_user_id)

    if check_user_id in get_guarantees():
        bot.send_photo(message.chat.id, 'https://imageup.ru/img205/4967023/1000012384.jpg', caption=f"""
🆔 Id: {check_user_id}
🔁 Репутация: Гарант
Шанс скама: 0%
🚮 Слито Скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
        return

    if rank == 'Скаммер':
        evidence, reason = get_scammers_info(check_user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img298/4967024/1000012382.jpg', caption=f"""
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
🆔 Id: {check_user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zayavki}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank in ['Администратор', 'Директор', 'Волонтёр']:
        bot.send_photo(message.chat.id, 'https://imageup.ru/img31/4967021/1000012386.jpg', caption=f"""
🆔 Id: {check_user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zayavki if rank in ['Администратор', 'Директор'] else slitoscammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    else:
        bot.send_photo(message.chat.id, 'https://imageup.ru/img1/4967020/1000012383.jpg', caption=f"""
Нету в базе:
🆔 Id: {check_user_id}
🔁 Репутация: Нету в базе
❓ Шанс скама: 50%
🚮 Слито Скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")

@bot.message_handler(commands=['checkmy'])
def cmd_check_my_status(message):
    user_id = message.from_user.id
    
    if user_id in get_guarantees():
        slitoscammerov = get_slitoscammerov(user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img205/4967023/1000012384.jpg', caption=f"""
🆔 Id: {user_id}
🔁 Репутация: Проверен гарантом
Шанс скама: 0%
🚮 Слито Скамеров: {slitoscammerov}
🔍 Искали в базе: {check_if_in_database(user_id)}
✅ Greenlight Base
""")
        return

    rank = check_user_rank(user_id)
    slitoscammerov = get_slitoscammerov(user_id)
    iskalivbase = check_if_in_database(user_id)

    if rank == 'Владелец':
        bot.send_photo(message.chat.id, 'https://imageup.ru/img31/4967021/1000012386.jpg', caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 0%
🚮 Заявки: {zayavki}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank in ['Администратор', 'Директор', 'Волонтёр']:
        bot.send_photo(message.chat.id, 'https://imageup.ru/img154/4967022/1000012388.jpg', caption=f"""
🆔 Id: {user_id}
🔁 Репутация: {rank}
Шанс скама: 10%
🚮 Заявки: {zayavki if rank in ['Администратор', 'Директор'] else slitoscammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")
    elif rank == 'Скаммер':
        evidence, reason = get_scammers_info(user_id)
        bot.send_photo(message.chat.id, 'https://imageup.ru/img298/4967024/1000012382.jpg', caption=f"""
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
Нету в базе:
🆔 Id: {user_id}
🔁 Репутация: Нету в базе
❓ Шанс скама: 50%
🚮 Слито Скамеров: {slitoscammerov}
🔍 Искали в базе: {iskalivbase}
✅ Greenlight Base
""")

@bot.message_handler(commands=['scam'])
def cmd_scam(message):
    if message.from_user.id not in ADMIN_ID and message.from_user.id not in OWNER_ID and message.from_user.id not in VOLUNTEER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        bot.reply_to(message, 'Используйте: /scam (юзернейм) (доказательства) (причина/возможный скам)')
        return

    username = args[1]
    evidence = args[2]
    reason = args[3]

    scam_user_id = get_user_id(username)
    if scam_user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    if 'возможный скам' in reason.lower():
        rank = 'Возможный скаммер'
    else:
        rank = 'Скаммер'

    add_to_scammers(scam_user_id, evidence, reason, rank)

    bot.reply_to(message, f'Пользователь {username} (ID: {scam_user_id}) был добавлен в базу скамеров как {rank}.\nДоказательства: {evidence}\nПричина: {reason}')

@bot.message_handler(commands=['noscam'])
def cmd_noscam(message):
    if message.from_user.id not in ADMIN_ID and message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Используйте: /noscam (юзерID) (причина)')
        return

    del_user_id = get_user_id(args[0])
    if del_user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    remove_user(del_user_id)
    bot.reply_to(message, f'Пользователь {del_user_id} удален из базы. Причина: {" ".join(args[1:])}.')

@bot.message_handler(commands=['trust'])
def cmd_revoke_trust(message):
    if message.from_user.id not in GARANT_ID and message.from_user.id not in OWNER_ID:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Используйте: /trust (юзернейм)')
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

@bot.message_handler(commands=['rank'])
def cmd_set_rank(message):
    if message.from_user.id not in OWNER_ID:  # Проверка прав доступа
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Используйте: /rank (юзерID) (ранг)')
        return

    user_id = get_user_id(args[0])
    if user_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    rank = args[1].lower()
    valid_ranks = ['скамер', 'гарант', 'администратор', 'волонтёр', 'директор', 'владелец']
    if rank not in valid_ranks:
        bot.reply_to(message, f'Недопустимый ранг. Доступные ранги: {", ".join(valid_ranks)}.')
        return

    # Логика для обновления ранга может быть добавлена здесь.
    if rank == 'гарант':
        add_to_guarantees(user_id)
    elif rank == 'администратор':
        add_admin(user_id)
    elif rank == 'волонтёр':
        add_volunteer(user_id)
    elif rank == 'директор':
        add_director(user_id)
    elif rank == 'владелец':
        # Логика для владельца, если такая требуется
        pass

    bot.reply_to(message, f'Ранг для пользователя {user_id} установлен на: {rank}.')

# Запуск бота с обработкой исключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
