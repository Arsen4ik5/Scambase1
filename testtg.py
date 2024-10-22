
import telebot
import random

API_TOKEN = '7849780225:AAH5DUyAubUmpLPFVEvv0vfD3IDbPHgDJ9c'  # Замените на токен вашего бота
bot = telebot.TeleBot(API_TOKEN)

# Глобальные переменные
reports = {}
admins = {6321157988}  # ID создателя бота
guarantees = {}
scammers = set()

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

    report_id = int(args[1])
    rank = args[2].lower()

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

    new_admin = int(args[1])
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

    user_id = int(args[1])
    if user_id in scammers:
        rank = "скамер"
    elif user_id in guarantees:
        rank = "гарант"
    else:
        rank = "петух"

    bot.send_message(message.chat.id, f'Пользователь {user_id}: Ранг - {rank}.')

# Команда /addgarant для добавления гаранта
@bot.message_handler(commands=['addgarant'])
def add_garant(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, 'Укажите ID пользователя для добавления в гарант.')
        return

    garant_id = int(args[1])
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

    bot.send_message(message.chat.id, f'Ваш ID: {user_id}, Ранг: {rank}.')

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)


### Пояснения к коду

1. **Команда `/report`**: Пользователь может подать жалобу, и бот выдает уникальный номер для этой жалобы.

2. **Команда `/acceptreport`**: Администратор принимает жалобу, устанавливает ранг (скамер или гарант), и, если это скам, добавляет пользователя в список мошенников.

3. **Команда `/addadm`**: Позволяет администратору добавлять других администраторов с защитой от повторного добавления.

4. **Команда `/check`**: Проверяет статус пользователя по ID и сообщает его ранг (скамер, гарант или петух).

5. **Команда `/addgarant`**: Позволяет добавлять пользователя в список гарантов.

6. **Команда `/checkmy`**: Позволяет пользователю проверять свой статус и ранг.

### Что нужно сделать

1. Замените `YOUR_API_TOKEN` на токен вашего бота.

2. Запустите скрипт, и бот будет готов к использованию.

### Примечания

- Перед использованием убедитесь, что у вас есть необходимые права и соглашения на обработку данных пользователей.
- В этом коде не предусмотрена сложная обработка ошибок и валидация ввода — вы можете улучшить его по мере необходимости.
- Поскольку бот работает в режиме `polling`, он будет ожидать сообщения и реагировать на команды.

Если у вас есть другие вопросы или требуется помощь, дайте знать!КопироватьПоделиться с друзьями
Вы (13:16:29): Напиши бота на тг на библеотеке телебот для написания жалобы по команде /report юз который выдаёт номер для принятии жалобы админом по команде /acceptrepport по номеру админ добавляется другим админом по команде /addadm и комманда /check которая проверяет процент обмана занесён ли человек в мошенники и даёт ранг по таким типам как (скамер,петух,или же гарант) добавление гаранта id создателя (тоесть админа) в тг 7451036519 и команда /checkmy спомощью которой можно проверить себя (статус пользователя) при этом он должен выдавать инфу о пользователе так (🔎Результат поиска: 🔥Репутация: 🆔Айди: 🧐Юзер:)
ChatGPT (13:16:58): Вот пример кода для создания Telegram-бота, который удовлетворяет всем вашим требованиям с использованием библиотеки `telebot` (pyTelegramBotAPI). Этот код включает команды для подачи жалобы, принятия жалобы, добавления администраторов, проверки статуса пользователей и добавления гарантов. Бот будет выводить информацию о пользователе в формате, который вы указали.

### Установка библиотеки

Если у вас еще нет `telebot`, выполните следующую команду:

bash
pip install pyTelegramBotAPI


### Пример кода

python
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
