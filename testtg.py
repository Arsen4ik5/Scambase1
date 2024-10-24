import telebot
import random
import time
import requests

API_TOKEN = '7275319279:AAGZh_GzI4iO5Vsb3lcBsF0RLUq5Meh-yh8'  # Замените на токен вашего бота
ADMIN_ID = 6321157988  # ID создателя бота

bot = telebot.TeleBot(API_TOKEN)

reports = {}
admins = {ADMIN_ID}
guarantees = {}
scammers = set()

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
                 /delbase (юзерID) (причина) - Удалить из базы""")

def get_user_id(param):
    """Получение ID пользователя по username или ID."""
    try:
        if param.isdigit():
            return int(param)
        else:
            user = bot.get_chat(param)
            return user.id if user else None
    except Exception:
        return None

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
    if message.from_user.id not in admins:
        bot.reply_to(message, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(message, 'Укажите номер жалобы и ранг (скамер, петух, гарант).')
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
            scammers.add(reports[report_id]['user_id'])
        elif rank == 'гарант':
            guarantees[reports[report_id]['user_id']] = True

        bot.reply_to(message, f'Жалоба {report_id} принята. Ранг установлен: {rank}.')
    else:
        bot.reply_to(message, 'Такой жалобы не существует.')

@bot.message_handler(commands=['addadm'])
def cmd_add_admin(message):
    if message.from_user.id not in admins:
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

    admins.add(new_admin)
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
    
    rank = 'Нету в базе'
    if check_user_id in scammers:
        rank = 'скамер'
    elif check_user_id in guarantees:
        rank = 'гарант'
    
    username = f"ID: {check_user_id}"  # Замените на логику для получения username

    bot.reply_to(message, 
                  f"🔎Результат поиска:\n"
                  f"🔥Репутация: {rank}\n"
                  f"🆔Айди: {check_user_id}\n")

@bot.message_handler(commands=['checkmy'])
def cmd_check_my_status(message):
    user_id = message.from_user.id
    rank = 'Нету в базе'

    if user_id in scammers:
        rank = 'скамер'
    elif user_id in guarantees:
        rank = 'гарант'

    username = f"ID: {user_id}"  # Замените на логику для получения username

    bot.reply_to(message, 
                  f"🔎Результат поиска:\n"
                  f"🔥Репутация: {rank}\n"
                  f"🆔Айди: {user_id}\n  ")

@bot.message_handler(commands=['addgarant'])
def cmd_add_garant(message):
    args = message.text.split()[1:]
    if len(args) < 1:
        bot.reply_to(message, 'Укажите ID пользователя для добавления в гарант.')
        return

    garant_id = get_user_id(args[0])
    if garant_id is None:
        bot.reply_to(message, 'Некорректный ID или username.')
        return

    guarantees[garant_id] = True
    bot.reply_to(message, f'Пользователь {garant_id} добавлен как гарант.')

@bot.message_handler(commands=['delbase'])
def cmd_del_base(message):
    if message.from_user.id not in admins:
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

    # Удаление пользователя из базы (возврат статуса)
    if del_user_id in scammers:
        scammers.remove(del_user_id)
    if del_user_id in guarantees:
        guarantees.pop(del_user_id, None)

    bot.reply_to(message, f'Пользователь {del_user_id} удален из базы. Причина: {" ".join(args[1:])}. Статус возвращен: Нету в базе.')

# Запуск бота с обработкой исключений
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
