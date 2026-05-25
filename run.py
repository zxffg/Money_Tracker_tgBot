from aiogram import Bot, Dispatcher

from app.handlers import router

import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

#! Запуск бота и обработка ошибок
async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('bot exit')