import os
import asyncio
from typing import List, Dict
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from database.database import Database
import logging
from logger.logger_config import setup_logging
from .keyboard import get_main_keyboard, get_exercise_keyboard, get_back_keyboard

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)
db = Database()
router = Router()


async def main():
    logger.info("Инициализация базы данных")
    await db.create_pool()
    await db.init_tables()

    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Бот запускается")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
