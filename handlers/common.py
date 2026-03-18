import csv
import random

from datetime import timedelta 

from aiogram import types, Router, F, Bot
from aiogram.filters import CommandStart, Command

from databases.database import usernames
from databases.json_manager import load_actions, load_users, save_user

common_router = Router()

ACTIONS = load_actions()
Users = load_users()

complements = []
with open('databases/комплименты.csv', 'r', encoding='UTF-8') as comp:
    for i in csv.reader(comp):
        complements.append(''.join(i))

def find_user(message: types.Message):
    args = message.text.split()
    if len(args) >= 2 and args[1].startswith('@'):
        return args[1][1:]
    return None

@common_router.message(Command("помощь", prefix="!"))
async def help_cmd(message: types.Message):
    await message.answer(
    "📖 Доступные команды:\n\n"
    "ЛС бота:\n"
    "/start - начать использовать бота (В ЛС БОТУ)\n"
    "!игра21 - 2 правды 1 ложь (В ЛС БОТУ)\n"
    "!анон - Анонимный факт о себе (В ЛС БОТУ):\n\n"
    "Основные:\n"
    "!помощь — Список команд\n"
    "!профиль [@username] — Информация об участнике ША2\n"
    "!вероятность — Рассчитывает вероятность события\n"
    "!цитата — Сохраняет цитату (ответом на сообщение)\n"
    "!мысль — Выводит рандомную цитату\n"
    "!мысль [@username] — Цитата конкретного пользователя\n"
    "!кто — Узнать, кто больше всего соответствует запросу\n"
    "!совместимость — Показывает совместимость чего-либо\n"
    "!комплимент — Сделать комплимент пользователю\n"
    "!рулетка — Испытай удачу\n"
    "!анмут — Размут пользоватея. Используйте ответом на сообщение\n"
    "!кто это - Угадай участника по 2 фактам\n"
    "!до проекта - время до проекта\n"
    "\n"
    "Интерактивные команды:\n"
    "!обнять [@username]\n"
    "!пожать_руку [@username]\n"
    "!погладить [@username]\n"
    "!похвалить [@username]\n"
    "!поддержать [@username]\n"
    "!поблагодарить [@username]\n"
    "!поздравить [@username]\n"
    "!тыкнуть [@username]\n"
    "!посмотреть [@username]\n"
    "!уважать [@username]\n"
    "!аплодировать [@username]"
)

@common_router.message(Command('анмут', prefix="!"))
async def unmute_cmd(message: types.Message, bot: Bot):
    if message.reply_to_message:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.reply_to_message.from_user.id,
            permissions=types.ChatPermissions(can_send_messages=True)
        )
        await message.reply('Сделал')
    else:
        for user_id in Users.keys():
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=types.ChatPermissions(can_send_messages=True)
            )
        await message.reply('Все пользователи размучены')

@common_router.message(Command('вероятность', prefix="!"))
async def chance_cmd(message: types.Message):
    event = message.text.replace('!вероятность', '', 1).strip()
    chance = random.randint(0, 100)
    if not event:
        await message.reply('Напишите событие')
    else:
        await message.reply(f'Вероятность {event} - {chance}%')

@common_router.message(Command('мысль', prefix="!"))
async def thought_cmd(message: types.Message):
    thoughts = []
    with open('databases/цитаты.csv', 'r', encoding='UTF-8') as file:
        reader = csv.reader(file)
        for row in reader:
            thoughts.append(row)

    args = message.text.split()
    if len(args) > 2:
        await message.reply('Вы неправильно использовали команду\nПопробуйте снова')
    else:
        if len(args) == 1:
            random_thought = random.choice(thoughts)
            thought, author = random_thought
            await message.reply(
                f'«{thought}»\n\n'
                f'Автор: @{author}'
            )
        elif len(args) == 2 and args[1].startswith('@'):
            user = args[1][1:]
            userquotes = [x for x in thoughts if user in x]
            random_thought = random.choice(userquotes)
            thought, author = random_thought
            await message.reply(
                f'«{thought}»\n\n'
                f'Автор: @{author}'
            )


@common_router.message(Command('цитата', prefix="!"))
async def quote_cmd(message: types.Message):
    quote = message.reply_to_message.text
    user = message.reply_to_message.from_user.username
    if quote == None:
        await message.reply('Используйте ответом на сообщение')
    else:
        with open('databases/цитаты.csv', 'a', encoding='UTF-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([quote, user])

        await message.reply(
            f'💾 Цитата сохранена!\n\n'
            f"«{quote}»\n\n"
            f"Автор: @{user}"
        )

@common_router.message(Command('кто', prefix="!"))
async def who_cmd(message: types.Message):
    question = message.text.split()
    who = random.choice(usernames())[0]
    if len(question) < 2:
        await message.reply('Вы неправильно использовали команду\nПопробуйте снова')
    else:
        question.remove('!кто')
        a = ' '.join(question)
        await message.reply(
            f'@{who} {a}'
        )

@common_router.message(Command('комплимент', prefix="!"))
async def complement_cmd(message: types.Message):
    user = None
    if message.reply_to_message:
        user = message.reply_to_message.from_user.username
    else:
        args = message.text.split()
        if len(args) > 1 and args[1].startswith('@'):
            user = args[1][1:]
    if not user:
        await message.reply(
            "❗ Используй:\n"
            "!комплимент ответом на сообщение\n"
            "!комплимент @username"
        )
    else:
        complement = random.choice(complements)
        await message.reply(f'@{user} {complement}')

@common_router.message(Command('совместимость', prefix="!"))
async def compatibility_cmd(message: types.Message):
    event = message.text.replace('!совместимость', '', 1).strip()
    compatibility = random.randint(0, 100)
    if not event:
        await message.reply('Напишите событие')
    else:
        await message.reply(f'Совместимость {event} - {compatibility}%')

@common_router.message(Command('рулетка', prefix="!"))
async def roulette_cmd(message: types.Message, bot: Bot):
    a = message.from_user
    save_user(a.id, a.username)
    chance = random.randint(1, 6)
    if chance == 1:
        until_date = message.date + timedelta(minutes=5)
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
        await message.reply(
            'Тебе сегодня явно не везет\n'
            'Ты поймал мут на 5 минут'
        )
    else:
        await message.reply(
            'Везунчик, живешь без мута\n'
            'Попробуй еще раз'
        )


@common_router.message()
async def action_cmd(message: types.Message):
    # сохраняем пользователя
    user = message.from_user
    if user.username:
        save_user(user.id, user.username)

    # проверяем что это команда
    if not message.text or not message.text.startswith('!'):
        return

    command = message.text.split()[0][1:].lower().strip()

    if command not in ACTIONS:
        return

    # ищем пользователя
    to_user = find_user(message)
    from_user = message.from_user.username or message.from_user.first_name

    if not to_user:
        await message.reply(
            'Введите в формате\n'
            '![действие] @username'
        )
        return

    text = random.choice(ACTIONS[command]).format(
        from_user=from_user,
        to_user=to_user
    )

    await message.reply(text)