import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from dotenv import load_dotenv

from bot.handlers import register, user, admin

from bot.middlewares.db import DataBaseSession
from db.database import session_maker

load_dotenv()

TOKEN = os.getenv('TOKEN')


async def main():
    bot = Bot(token=TOKEN, parse_mode='HTML')

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(register.router)
    dp.include_router(user.router)
    dp.include_router(admin.router)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
