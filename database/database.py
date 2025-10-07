from anaconda_catalogs.catalog import USER_AGENT
import asyncpg
from typing import Optional, Dict, Any, List
import os
import logging
from configs.logger_config import setup_logging
from configs.config_reader import config


setup_logging()
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
            'database': config.db_name,
            'user': config.db_user,
            'password': config.db_password.get_secret_value(),
            'host': config.db_host,
            'port': config.db_port
        }
    
    # TODO добавить docstring
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

    # TODO добавить docstring
    async def init_tables(self) -> None:
        """
        Инициализация таблиц
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                CREATE TABLE IF NOT EXISTS "USER" (
                    id SERIAL PRIMARY KEY,
                    telegram_id INTEGER UNIQUE NOT NULL
                )
                ''')
                await conn.execute('''
                CREATE TABLE IF NOT EXISTS WORKOUT (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL REFERENCES "USER"(id),
                    date DATE NOT NULL DEFAULT CURRENT_DATE
                )
                ''')
                await conn.execute('''
                CREATE TABLE IF NOT EXISTS EXERCISE (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL REFERENCES "USER"(id),
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
        except Exception as e:
            logging.critical(f"Критическая ошибка при создании таблицы {e}")

    # TODO добавить docstring
    async def _fill_exercises(self, user_id):
        """
        Заполнение таблицы упражнений базовыми данными
        """
        try:
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
                    async with self.pool.acquire() as conn:
                        await conn.execute('''
                        INSERT INTO EXERCISE (name, muscle_group, user_id)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (name) DO NOTHING
                        ''', name, muscle, user_id)
            logger.info("База данных заполнена успешно")
        except Exception as e:
            logger.critical(f"Ошибка заполнения базы данных: {e}")
            raise

    # TODO добавить docstring
    async def get_create_user(self, telegram_id) -> int:
        """
        Получить или создать пользователя
        """
        try:
            async with self.pool.acquire() as conn:
                user_id = await conn.fetchval('''
                    INSERT INTO "USER" (telegram_id)
                    VALUES ($1)
                    ON CONFLICT (telegram_id)
                    DO UPDATE SET
                        telegram_id = EXCLUDED.telegram_id
                    RETURNING id
                    ''', telegram_id)
                logger.info("Пользователь создан или получен")
                return user_id
        except Exception as e:
            logger.critical(f"Ошибка при получении или создании пользователя: {e}")
            raise

    # TODO добавить docstring
    async def create_workout(self, user_id: int) -> int:
        """
        Создать новую тренировку
        """
        try:
            async with self.pool.acquire() as conn:
                workout_id = await conn.fetchval('''
                    INSERT INTO WORKOUT (user_id)
                    VALUES ($1)
                    RETURNING id
                    ''', user_id)
                logger.info("Тренировка успешно создана")
                return workout_id
        except Exception as e:
            logger.critical(f"Ошибка при создании тренировки: {e}")
            raise
    
    # TODO добавить docstring
    async def create_exercise(self, muscle_group: str, name: str, user_id: int) -> int:
        """
        Создать новое упражнение
        """
        try:
            async with self.pool.acquire() as conn:
                exercise_id = await conn.fetchval('''
                    INSERT INTO EXERCISE (name, muscle_group, user_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                    ''', name, muscle_group, user_id)
                logger.info("Упражнение успешно создано")
                return exercise_id
        except Exception as e:
            logger.critical(f"Ошибка при создании упражнения: {e}")
            raise
    
    # TODO добавить docstring
    async def get_exercises_by_muscle_group(self, user_id: int, muscle_group: str) -> List[str]:
        """
        Получить упражнения пользователя
        """
        try:
            async with self.pool.acquire() as conn:
                exercises = await conn.fetch('''
                    SELECT e.name FROM EXERCISE e
                    WHERE e.user_id = $1 AND e.muscle_group = $2
                    ''', user_id, muscle_group)
                logger.info("Упражнения успешно получены")
                return [row['name'] for row in exercises]
        except Exception as e:
            logger.critical(f"Ошибка при получении упражнении: {e}")
            raise
    
    # TODO добавить docstring
    async def get_muscle_groups(self, user_id: int) -> List[str]:
        """
        Получить группы мышц пользователя
        """
        try:
            async with self.pool.acquire() as conn:
                muscle_groups = await conn.fetch('''
                    SELECT DISTINCT e.muscle_group FROM EXERCISE e
                    WHERE e.user_id = $1
                    ORDER BY e.muscle_group
                    ''', user_id)
                logger.info("Группы мышц успешно получены")
                return [row['muscle_group'] for row in muscle_groups]
        except Exception as e:
            logger.critical(f"Ошибка при получении групп мышц: {e}")
            raise

    # # TODO переписать
    async def get_user_workouts(self, user_id: int, limit: int = 1) -> List[Dict]:
        """
        Получить тренировки пользователя
        """
        async with self.pool.acquire() as conn:
            workouts = await conn.fetch('''
            SELECT w.id, w.date,
                    COUNT(s.id) as exercise_count,
                    SUM(s.weight * s.reps) as total_volume
            FROM WORKOUT w
            LEFT JOIN SET s ON w.id = s.workout_id
            WHERE w.user_id = $1
            GROUP BY w.id, w.date
            ORDER BY w.date DESC
            LIMIT $2
            ''', user_id, limit)
            return [dict(w) for w in workouts]

    # TODO добавить docstring
    async def add_set_to_workout(self, workout_id: int, exercise_id: int,
                                set_order: int, weight: float, reps: int) -> int:
        """Добавить подход к тренировке"""
        try:
            async with self.pool.acquire() as conn:
                set_id = await conn.fetchval('''
                INSERT INTO SET (workout_id, exercise_id, set_order, weight, reps)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                ''', workout_id, exercise_id, set_order, weight, reps)
                logger.info("Подход успешно добавлен")
                return set_id
        except Exception as e:
            logger.critical(f"Ошибка при добавлении подхода к тренировке: {e}")
            raise
    
    # TODO добавить docstring
    async def get_workout_sets(self, workout_id: int) -> List[Dict]:
        """
        Получить все подходы тренировки
        """
        try:
            async with self.pool.acquire() as conn:
                sets = await conn.fetch('''
                SELECT s.id, s.set_order, s.weight, s.reps,
                        e.name as exercise_name, e.muscle_group
                FROM SET s
                JOIN EXERCISE e ON s.exercise_id = e.id
                WHERE s.workout_id = $1
                ORDER BY s.set_order
                ''', workout_id)
                logger.info("Все подходы успешно получены")
                return [dict(s) for s in sets]
        except Exception as e:
            logger.critical(f"Ошибка при получении подходов: {e}")
            raise
