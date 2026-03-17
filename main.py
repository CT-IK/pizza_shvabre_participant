import asyncio
import os

from aiogram import Bot, Dispatcher

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from handlers.private_cmd import private_router
from handlers.group_cmd import group_router
from handlers.auto_cmd import auto_router
from handlers.common import common_router

ALLOWED_UPDATES = ['message']

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()

dp.include_router(private_router)
dp.include_router(group_router)
dp.include_router(auto_router)
dp.include_router(common_router)


async def main():
    print('Бот работает')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    asyncio.run(main())