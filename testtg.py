
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

API_TOKEN = 'YOUR_API_TOKEN'  # Замените на токен вашего бота
ADMIN_ID = 7451036519  # ID создателя бота

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

reports = {}
admins = {ADMIN_ID}
guarantees = {}
scammers = set()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Используйте следующие команды:\n"
                        "/report (юзерID) (причина) - Подать жалобу\n"
                        "/acceptreport (номер) (ранг) - Принять жалобу\n"
                        "/addadm (юзерID/username) - Добавить админа\n"
                        "/check (юзерID/username) - Проверить репутацию\n"
                        "/checkmy - Проверить свой статус\n"
                        "/addgarant (юзерID/username) - Сделать гарантом")

def get_user_id(param: str):
    """Получение ID пользователя по username или через прямой ID."""
    if param.isdigit():
        return int(param)
    else:
        user = bot.get_user(param)  # Эта часть должна уточнять как получить ID по username
        return user.id if user else None

@dp.message_handler(commands=['report'])
async def cmd_report(message: types.Message):
    args = message.get_args().split()
    if len(args) < 2:
        await message.reply("Используйте: /report (юзерID/username) (причина)")
        return
    reported_user_id = get_user_id(args[0])
    if reported_user_id is None:
        await message.reply("Некорректный ID или username.")
        return
    reason = ' '.join(args[1:])
    report_id = random.randint(10000, 99999)
    reports[report_id] = {'user_id': reported_user_id, 'status': 'pending', 'reason': reason, 'rank': None}
    await message.reply(f'Ваша жалоба подана. Номер жалобы: {report_id}')

@dp.message_handler(commands=['acceptreport'])
async def cmd_accept_report(message: types.Message):
    if message.from_user.id not in admins:
        await message.reply('У вас нет прав для выполнения этой команды.')
        return
    args = message.get_args().split()
    if len(args) < 2:
        await message.reply('Укажите номер жалобы и ранг (скамер, петух, гарант).')
        return
    try:
        report_id = int(args[0])
        rank = args[1].lower()
    except ValueError:
        await message.reply('Некорректный ввод. Убедитесь, что номер жалобы — это число.')
        return
    if report_id in reports:
        reports[report_id]['status'] = 'accepted'
        reports[report_id]['rank'] = rank
        if rank == 'скамер':
            scammers.add(reports[report_id]['user_id'])
        elif rank == 'гарант':
            guarantees[reports[report_id]['user_id']] = True
        await message.reply(f'Жалоба {report_id} принята. Ранг установлен: {rank}.')
    else:
        await message.reply('Такой жалобы не существует.')

@dp.message_handler(commands=['addadm'])
async def cmd_add_admin(message: types.Message):
    if message.from_user.id not in admins:
        await message.reply('У вас нет прав для выполнения этой команды.')
        return
    args = message.get_args().split()
    if len(args) < 1:
        await message.reply('Укажите ID пользователя или username для добавления в администраторы.')
        return
    new_admin = get_user_id(args[0])
    if new_admin is None:
        await message.reply('Некорректный ID или username.')
        return
    admins.add(new_admin)
    await message.reply(f'Пользователь {new_admin} добавлен как администратор.')

@dp.message_handler(commands=['check'])
async def cmd_check(message: types.Message):
    args = message.get_args().split()
    if len(args) < 1:
        await message.reply('Укажите ID пользователя или username для проверки.')
        return
    check_user_id = get_user_id(args[0])
    if check_user_id is None:
        await message.reply('Некорректный ID или username.')
        return
    rank = 'петух'
    if check_user_id in scammers:
        rank = 'скамер'
    elif check_user_id in guarantees:
        rank = 'гарант'
    # Получаем username
    username = await get_username(check_user_id)
    await message.reply(f"🔎Результат поиска:\n\n🔥Репутация: {rank}\n\n🆔Айди: {check_user_id}\n🧐Юзер: @{username}")

async def get_username(user_id):
    try:
        user = await bot.get_chat(user_id)
        return user.username if user.username else "Нет юзернейма"
    except:
        return "Нет юзернейма"

@dp.message_handler(commands=['checkmy'])
async def cmd_check_my_status(message: types.Message):
    user_id = message.from_user.id
    rank = 'Нету в базе'
    if user_id in scammers:
        rank = 'скамер'
    elif user_id in guarantees:
        rank = 'гарант'
    username = await get_username(user_id)
    await message.reply(f"🔎Результат поиска:\n\n🔥Репутация: {rank}\n\n🆔Айди: {user_id}\n🧐Юзер: @{username}")

@dp.message_handler(commands=['addgarant'])
async def cmd_add_garant(message: types.Message):
    args = message.get_args().split()
    if len(args) < 1:
        await message.reply('Укажите ID пользователя или username для добавления в гарант.')
        return
    garant_id = get_user_id(args[0])
    if garant_id is None:
        await message.reply('Некорректный ID или username.')
        return
    guarantees[garant_id] = True
    await message.reply(f'Пользователь {garant_id} добавлен как гарант.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
