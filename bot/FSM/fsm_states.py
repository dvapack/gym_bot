from aiogram.fsm.state import StatesGroup, State
from database.database import Database
from typing import List

db: Database = None

async def load_muscle_groups(user_id: int) -> List[str]:
    """
    Загрузка доступных групп мышц из базы данных

    Args:
        user_id (int): Идентификатор пользователя

    Returns:
        available_muscle_groups (List[str]): Список доступных групп мышц
    """
    if db is None or db.pool is None:
        available_muscle_groups = []
        return available_muscle_groups
    available_muscle_groups = await db.get_muscle_groups(user_id)
    return available_muscle_groups

async def load_exercises(user_id: int, muscle_group: str) -> List[str]:
    """
    Загрузка доступных упражнений из базы данных

    Args:
        user_id (int): Идентификатор пользователя
        muscle_group (str): Группа мышц, для которой нужны упражнения

    Returns:
        available_exercises (List[str]): Список доступных упражнений для выбранной группы мышц
    """
    if db is None or db.pool is None:
        available_exercises = []
        return available_exercises
    available_exercises = await db.get_exercises_by_muscle_group(user_id, muscle_group)
    return available_exercises
    
class States(StatesGroup):
    choosing_muscle_group = State()
    adding_muscle_group = State()
    choosing_exercise = State()
    adding_exercise = State()
    entering_weight = State()
    entering_repeats = State()
