import asyncio
import random
from datetime import datetime, time, timedelta

from aiogram import types, Router
from databases.database import get_usernames

auto_router = Router()

TAGS = ["#райтнау", "#музрайтнау"]  # Теги для постов
POSTS_PER_DAY = 2  # Каждого тега в день
USERS_TO_TAG = 3   # Количество случайных пользователей

async def schedule_daily_posts(bot: types.Bot, chat_id: int):
    """
    Фоновая задача для ежедневных автоматических постов с тегами.
    """
    while True:
        now = datetime.now()
        today_start = datetime.combine(now.date(), time(hour=8))
        today_end = datetime.combine(now.date(), time(hour=22))

        # Список запланированных времён для постов (рандомные в пределах дня)
        post_times = sorted([
            today_start + timedelta(seconds=random.randint(0, int((today_end - today_start).total_seconds())))
            for _ in range(POSTS_PER_DAY * len(TAGS))
        ])

        for post_time, tag in zip(post_times * len(TAGS), TAGS * POSTS_PER_DAY):
            delay = (post_time - datetime.now()).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)

            # Берём 3 случайных пользователя
            usernames = [u[0] for u in get_usernames()]
            tagged_users = random.sample(usernames, min(len(usernames), USERS_TO_TAG))
            mention_text = " ".join(f"@{u}" for u in tagged_users)

            # Отправляем сообщение в чат
            await bot.send_message(
                chat_id=chat_id,
                text=f"{tag} {mention_text}"
            )

        # Ждём до следующего дня
        tomorrow_start = datetime.combine(now.date() + timedelta(days=1), time(hour=8))
        await asyncio.sleep((tomorrow_start - datetime.now()).total_seconds())

# Команда для запуска фоновой задачи
@auto_router.message(commands=["автопосты"])
async def start_auto_posts(message: types.Message):
    await message.reply("Запуск ежедневных автоматических постов #райтнау и #музрайтнау 🚀")
    asyncio.create_task(schedule_daily_posts(message.bot, message.chat.id))