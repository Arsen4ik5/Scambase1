
import telebot
import random

API_TOKEN = 'YOUR_API_TOKEN'  # Замените на токен вашего бота
bot = telebot.TeleBot(API_TOKEN)

# Глобальные переменные
reports = {}
admins = {7451036519}  # ID создателя бота
guarantees = {}  # Гаранты
scammers = set()  # Мошенники

# Команда /report для подачи жалобы
@bot.message_handler(commands=['report'])
def report(message):
    user_id = message.from_user.id
    report_id = random.randint(10000, 99999)
    reports[report_id] = {'user_id': user_id, 'status': 'pending', 'rank': None}
    bot.send_message(message.chat.id, f'Ваша жалоба подана. Номер жалобы: {report_id}')

# Команда /acceptreport для принятия жалобы администратором
@bot.message_handler(commands=['acceptreport'])
def accept_report(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()
    if len(args) < 3:
        bot.send_message(message.chat.id, 'Укажите номер жалобы и ранг (скамер или гарант).')
        return

    try:
        report_id = int(args[1])
        rank = args[2].lower()
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректный ввод. Убедитесь, что номер жалобы — число.')
        return

    if report_id in reports:
        reports[report_id]['status'] = 'accepted'
        reports[report_id]['rank'] = rank

        if rank == 'скамер':
            scammers.add(reports[report_id]['user_id'])

        bot.send_message(message.chat.id, f'Жалоба {report_id} принята. Ранг установлен: {rank}.')
    else:
        bot.send_message(message.chat.id, 'Такой жалобы не существует.')

# Команда /addadm для добавления нового администратора
@bot.message_handler(commands=['addadm'])
def add_admin(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, 'У вас нет прав для выполнения этой команды.')
        return

    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, 'Укажите ID пользователя для добавления в администраторы.')
        return

    try:
        new_admin = int(args[1])
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректный ввод. Убедитесь, что ID — это число.')
        return

    if new_admin not in admins:
        admins.add(new_admin)
        bot.send_message(message.chat.id, f'Пользователь {new_admin} добавлен как администратор.')
    else:
        bot.send_message(message.chat.id, 'Этот пользователь уже является администратором.')

# Команда /check для проверки статуса пользователя
@bot.message_handler(commands=['check'])
def check_user(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, 'Укажите ID пользователя для проверки.')
        return

    try:
        user_id = int(args[1])
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректный ввод. Убедитесь, что ID — это число.')
        return

    if user_id in scammers:
        rank = "скамер"
    elif user_id in guarantees:
        rank = "гарант"
    else:
        rank = "петух"

    bot.send_message(message.chat.id, f"🔎Результат поиска:\n\n🔥Репутация: {rank}\n\n🆔Айди: {user_id}\n🧐Юзер: @{user_id}")

# Команда /addgarant для добавления гаранта
@bot.message_handler(commands=['addgarant'])
def add_garant(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, 'Укажите ID пользователя для добавления в гарант.')
        return

    try:
        garant_id = int(args[1])
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректный ввод. Убедитесь, что ID — это число.')
        return

    if garant_id not in guarantees:
        guarantees[garant_id] = True
        bot.send_message(message.chat.id, f'Пользователь {garant_id} добавлен как гарант.')
    else:
        bot.send_message(message.chat.id, 'Этот пользователь уже в списке гарантов.')

# Команда /checkmy для проверки своего статуса
@bot.message_handler(commands=['checkmy'])
def check_my_status(message):
    user_id = message.from_user.id
    if user_id in scammers:
        rank = "скамер"
    elif user_id in guarantees:
        rank = "гарант"
    else:
        rank = "петух"

    bot.send_message(message.chat.id, f"🔎Результат поиска:\n\n🔥Репутация: {rank}\n\n🆔Айди: {user_id}\n🧐Юзер: @{message.from_user.username}")

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
