import logging
import asyncio

from aiogram import Bot, Dispatcher
from bot.handlers import user_input_handler, keyboard_handler
from bot.FSM import fsm_states

from database.database import Database

from configs.logger_config import setup_logging
from configs.config_reader import config



setup_logging()
logger = logging.getLogger(__name__)
db = Database()


async def main():
    logger.info("Инициализация базы данных")
    await db.create_pool()
    await db.init_tables()

    user_input_handler.db = db
    keyboard_handler.db = db
    fsm_states.db = db


    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    dp.include_routers(user_input_handler.router, keyboard_handler.router)

    logger.info("Бот запускается")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
