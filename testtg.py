import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Словарь для хранения жалоб
reports = {}
# Словарь для хранения администраторов
admins = {}
# Словарь для хранения статусов пользователей
user_statuses = {}

# ID создателя (администратора)
CREATOR_ID = 7451036519

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для жалоб.')

def report(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        update.message.reply_text('Используйте: /report (юзер) (причина)')
        return
    user = context.args[0]
    reason = ' '.join(context.args[1:])
    report_number = len(reports) + 1
    reports[report_number] = {'user': user, 'reason': reason}
    update.message.reply_text(f'Жалоба на {user} принята. Номер жалобы: {report_number}')

def accept_report(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text('Используйте: /acceptreport (номер)')
        return
    report_number = int(context.args[0])
    if report_number in reports:
        report = reports.pop(report_number)
        update.message.reply_text(f'Жалоба на {report["user"]} принята!\nПричина: {report["reason"]}')
    else:
        update.message.reply_text('Нет такой жалобы.')

def add_admin(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != CREATOR_ID:
        update.message.reply_text('Вы не имеете прав для добавления администраторов.')
        return
    
    if len(context.args) < 1:
        update.message.reply_text('Используйте: /addadm (юзер_id)')
        return
    user_id = int(context.args[0])
    admins[user_id] = True
    update.message.reply_text(f'Администратор с ID {user_id} добавлен.')

def check(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text('Используйте: /check (юзер)')
        return
    user = context.args[0]
    status = user_statuses.get(user, 'нету в базе')
    percentage = 0  # Здесь можно добавить логику для расчета процента обмана
    rank = "незначительный"  # Здесь можно установить логику для рангов

    update.message.reply_text(
        f"🔎Результат поиска:\n
"
        f"🔥Репутация: {percentage}%\n"
        f"🆔Айди: {user}\n"
        f"🧐Юзер: {user}\n"
        f"Ранг: {rank}"
    )

def check_my(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    status = user_statuses.get(user_id, 'нету в базе')
    update.message.reply_text(f"Статус пользователя: {status}")

def add_garant(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text('Используйте: /addgarant (юзер)')
        return
    user = context.args[0]
    user_statuses[user] = 'гарант'
    update.message.reply_text(f'Пользователь {user} теперь гарант.')

def main() -> None:
    # Вставьте свой токен
    updater = Updater("YOUR_TOKEN")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("report", report))
    dispatcher.add_handler(CommandHandler("acceptreport", accept_report))
    dispatcher.add_handler(CommandHandler("addadm", add_admin))
    dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("checkmy", check_my))
    dispatcher.add_handler(CommandHandler("addgarant", add_garant))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
