from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    """
    Основная клавиатура

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками: новая тренировка и мои тренировки
    """
    keyboard = [
        [
            InlineKeyboardButton(text="Новая тренировка", callback_data="new_workout"),
            InlineKeyboardButton(text="Мои тренировки", callback_data="my_workouts")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def start_workout_keyboard(muscle_groups: List[str]):
    """
    Клавиатура для новой тренировки

    Args:
        muscle_groups (List[str]): Мышечные группы

    Returns:
        InlineKeyboardMarkup: Клавиатура с выбором мышечной группы или добавлением новой
    """
    keyboard = []
    for muscle_group in muscle_groups:
        keyboard.append([InlineKeyboardButton(text=muscle_group, callback_data=f"select_muscle_group:{muscle_group}")])
    keyboard.append([InlineKeyboardButton(text="Новая группа мышц", callback_data="new_muscle_group")])
    keyboard.append([InlineKeyboardButton(text="Завершить тренировку", callback_data="finish_workout")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_exercise_keyboard(exercises: List[str]):
    """
    Клавиатура для выбора упражнения

    Returns:
        InlineKeyboardMarkup: Клавиатура с выбором упражнения или добавлением нового
    """
    keyboard = []
    for exercise in exercises:
        keyboard.append([InlineKeyboardButton(text=exercise, callback_data=f"select_exercise:{exercise}")])
    keyboard.append([InlineKeyboardButton(text="Новое упражнение", callback_data="new_exercise")])
    keyboard.append([InlineKeyboardButton(text="Завершить тренировку", callback_data="finish_workout")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_muscle_group")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_to_exercises():
    """
    Клавиатура для возврата к упражнениям или для завершения тренировки

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой назад и завершением тренировки
    """
    keyboard = [
        [InlineKeyboardButton(text="Завершить тренировку", callback_data="finish_workout")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_exercise")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_last_workouts_keyboard(workouts: List[str]):
    """
    Клавиатура для выбора тренировки

    Args:
        workouts (List[str]): Список с датами тренировок

    Returns:
        InlineKeyboardMarkup: Клавиатура с выбором тренировки
    """
    keyboard = []
    for date in workouts:
        keyboard.append([InlineKeyboardButton(text=date, callback_data=f"get_workout:{date}")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_from_workout_view():
    """
    Клавиатура для выхода из просмотра тренировки

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой назад и выходом в главное меню
    """
    keyboard = [
        [InlineKeyboardButton(text="В главное меню", callback_data="back_to_main")],
        [InlineKeyboardButton(text="Назад", callback_data="my_workouts")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)