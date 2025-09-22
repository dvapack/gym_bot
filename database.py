from anaconda_catalogs.catalog import USER_AGENT
import asyncpg
import asyncio
from typing import Optional, Dict, Any, List
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def get_connection_params(self) -> Dict[str, Any]:
        """
        Получение параметров подключения из переменных окружения

        Returns:
            Dict[str, Any]: Параметры подключения к базе данных
        """
        return {
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }

    async def create_pool(self) -> None:
        """
        Создание пула соединений
        """
        try:
            params = await self.get_connection_params()
            self.pool = await asyncpg.create_pool(
                **params,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Пул соединений с PostgreSQL создан успешно")
        except Exception as e:
            logger.critical(f"Ошибка создания пула соединений: {e}")
            raise

    async def _fill_exercises(self):
        """
        Заполнение таблицы упражнений базовыми данными
        """
        exercises = [
            ("Жим штанги лежа", "Грудь"),
            ("Приседания со штангой", "Ноги"),
            ("Становая тяга", "Спина"),
            ("Подтягивания", "Спина"),
            ("Отжимания", "Грудь"),
            ("Жим гантелей сидя", "Плечи"),
            ("Сгибания на бицепс", "Руки"),
            ("Французский жим", "Руки"),
            ("Выпады", "Ноги"),
            ("Планка", "Пресс")
        ]

        for name, muscle in exercises:
            await self.pool.execute('''
            INSERT INTO EXERCISE (name, muscle_group)
            VALUES ($1, $2)
            ON CONFLICT (name) DO NOTHING
            ''', name, muscle)

    async def init_tables(self) -> None:
        """
        Инициализация таблиц
        """
        try:
            await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS USER (
                id SERIAL PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL
            )
            ''')
            await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS WORKOUT (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL REFERENCES USER(id),
                date DATE NOT NULL DEFAULT CURRENT_DATE
            )
            ''')
            await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS EXERCISE (
                id SERIAL PRIMARY KEY,
                muscle_group VARCHAR(50),
                name VARCHAR(50)
            )
            ''')
            await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS SET (
                id SERIAL PRIMARY KEY,
                workout INTEGER UNIQUE NOT NULL REFERENCES WORKOUT(id) ON DELETE CASCADE,
                exercise INTEGER UNIQUE NOT NULL REFERENCES EXERCISE(id),
                set_order INTEGER NOT NULL,
                weight DECIMAL(3, 2),
                reps INTEGER NOT NULL
            )
            ''')
            logging.info("Таблица создана успешно")
            await self._fill_exercises()
            logging.info("В таблицу добавлены базовые упражнения")
        except Exception as e:
            logging.critical(f"Критическая ошибка при создании таблицы {e}")
