import asyncio
import logging
import os
from handlers import funcs
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.filters.text import Text

import openai  

logging.basicConfig(level=logging.INFO)

openai.api_key = os.getenv("TOKAI")

async def main():
    bot = Bot(token=os.getenv("TOKEN"), parse_mode="HTML")
    dp = Dispatcher()
    
    dp.include_router(funcs.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())