import random
import json
from datetime import datetime, timedelta

from aiogram import types, Router, F
from aiogram.filters import Command

from databases.database import get_participant, get_usernames
from databases.game21_db import load_games, save_game

group_router = Router()

@group_router.message(Command('профиль', prefix="!"))
async def profile_cmd(message: types.Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith('@'):
        username = args[1][1:]
    else:
        await message.reply(
            "❗ Используй:\n"
            "!профиль @username"
        )
        return
    
    userdata = get_participant(username)
    if userdata == None:
        text = 'Участник еще не заполнил профиль'
    else:
        text = (
        f"<b>ПРОФИЛЬ УЧАСТНИКА: </b>\n\n"
        f"<b>Имя:</b> {userdata[1]}\n"
        f"<b>Возраст:</b> {userdata[2]}\n"
        f"<b>Дата рождения:</b> {userdata[3]}\n"
        f"<b>Факультет:</b> {userdata[4]}\n"
        f"<b>Хобби:</b> {userdata[5]}\n"
        f"<b>Откуда приехал:</b> {userdata[6]}\n"
        f"<b>Метро:</b> {userdata[7]}\n"
        f"<b>Необычный факт:</b> {userdata[8]}\n"
        f"<b>Любимая фраза:</b> {userdata[9]}\n"
    )

    await message.reply(text, parse_mode="HTML")

@group_router.message(F.text == '!кто это')
async def whois_cmd(message: types.Message):
    usernames = get_usernames()
    username = random.choice(usernames)[0]
    userdata = get_participant(username)
    userdata = userdata[2:]
    user_rand = random.sample(userdata, 2)
    send = (
        'Игра: угадай участника по 2 фактам из профиля\n\n'
        f'1) {user_rand[0]}\n'
        f'2) {user_rand[1]}\n\n'
        'Пиши @username ответом на это сообщение'
    )
    sent_msg = await message.reply(
        'Игра: угадай участника по 2 фактам из профиля\n\n'
        f'1) {user_rand[0]}\n'
        f'2) {user_rand[1]}\n\n'
        'Пиши @username ответом на это сообщение'
    )

    save_game(sent_msg.message_id, {
        "type": "whois",
        "author": username
    })

@group_router.message(F.text == '!до проекта')
async def time_to_project(message: types.Message):
    project_start = datetime(year=2026, month=3, day=20, hour=9, minute=0)
    now = datetime.now()

    if now >= project_start:
        await message.reply("Проект уже начался! 🚀")
        return

    delta: timedelta = project_start - now
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    if days == 1:
        day_text = "день"
    elif 2 <= days <= 4:
        day_text = "дня"
    else:
        day_text = "дней"

    if hours == 1:
        hour_text = "час"
    elif 2 <= hours <= 4:
        hour_text = "часа"
    else:
        hour_text = "часов"

    if minutes == 1:
        minute_text = "минута"
    elif 2 <= minutes <= 4:
        minute_text = "минуты"
    else:
        minute_text = "минут"

    if days > 0:
        text = f"До начала проекта осталось: {days} {day_text} {hours} {hour_text} и {minutes} {minute_text} ⏳"
    elif hours > 0:
        text = f"До начала проекта осталось: {hours} {hour_text} и {minutes} {minute_text} ⏳"
    else:
        text = f"До начала проекта осталось: {minutes} {minute_text} ⏳"

    await message.reply(text)