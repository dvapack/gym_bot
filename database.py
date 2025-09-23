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

    async def _fill_exercises(self, conn):
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
            await conn.execute('''
            INSERT INTO EXERCISE (name, muscle_group)
            VALUES ($1, $2)
            ON CONFLICT (name) DO NOTHING
            ''', name, muscle)

    async def init_tables(self) -> None:
        """
        Инициализация таблиц
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                CREATE TABLE IF NOT EXISTS USER (
                    id SERIAL PRIMARY KEY,
                    telegram_id INTEGER UNIQUE NOT NULL
                )
                ''')
                await conn.execute('''
                CREATE TABLE IF NOT EXISTS WORKOUT (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL REFERENCES USER(id),
                    date DATE NOT NULL DEFAULT CURRENT_DATE
                )
                ''')
                await conn.execute('''
                CREATE TABLE IF NOT EXISTS EXERCISE (
                    id SERIAL PRIMARY KEY,
                    muscle_group VARCHAR(50),
                    name VARCHAR(50)
                )
                ''')
                await conn.execute('''
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
                await self._fill_exercises(conn)
                logging.info("В таблицу добавлены базовые упражнения")
        except Exception as e:
            logging.critical(f"Критическая ошибка при создании таблицы {e}")

    async def get_create_user(self, telegram_id) -> int:
        """
        Получить или создать пользователя
        """
        async with self.pool.acquire() as conn:
            user_id = await conn.fetchval('''
                INSERT INTO USER (telegram_id)
                VALUES ($1)
                ON CONFLICT (telegram_id)
                DO UPDATE SET
                    telegram_id = EXCLUDED.telegram_id
                RETURNING id
                ''', telegram_id)
            return user_id

    async def create_workout(self, user_id: int) -> int:
        """
        Создать новую тренировку
        """
        async with self.pool.acquire() as conn:
            workout_id = await conn.fetchval('''
            INSERT INTO WORKOUT (user_id)
            VALUES ($1)
            RETURNING id
            ''', user_id)
            return workout_id

    async def get_user_workouts(self, user_id: int, limit: int = 1) -> List[Dict]:
            """
            Получить последние тренировки пользователя
            """
            async with self.pool.acquire() as conn:
                workouts = await conn.fetch('''
                SELECT w.id, w.date,
                       COUNT(s.id) as exercise_count,
                       SUM(s.weight * s.reps) as total_volume
                FROM WORKOUT w
                LEFT JOIN "set" s ON w.id = s.workout_id
                WHERE w.user_id = $1
                GROUP BY w.id, w.date
                ORDER BY w.date DESC
                LIMIT $2
                ''', user_id, limit)
                return [dict(w) for w in workouts]

    async def add_set_to_workout(self, workout_id: int, exercise_id: int,
                                set_order: int, weight: float, reps: int) -> int:
        """Добавить подход к тренировке"""
        async with self.pool.acquire() as conn:
            set_id = await conn.fetchval('''
            INSERT INTO SET (workout_id, exercise_id, set_order, weight, reps)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            ''', workout_id, exercise_id, set_order, weight, reps)
            return set_id

    async def get_workout_sets(self, workout_id: int) -> List[Dict]:
        """
        Получить все подходы тренировки
        """
        async with self.pool.acquire() as conn:
            sets = await conn.fetch('''
            SELECT s.id, s.set_order, s.weight, s.reps,
                    e.name as exercise_name, e.muscle_group
            FROM SET s
            JOIN EXERCISE e ON s.exercise_id = e.id
            WHERE s.workout_id = $1
            ORDER BY s.set_order
            ''', workout_id)
            return [dict(s) for s in sets]

    async def get_workout_details(self, workout_id: int) -> Dict:
        """
        Получить детальную информацию о тренировке
        """
        async with self.pool.acquire() as conn:
            workout = await conn.fetchrow('''
            SELECT w.*
            FROM WORKOUT w
            JOIN USER u ON w.user_id = u.id
            WHERE w.id = $1
            ''', workout_id)
            return dict(workout) if workout else None
