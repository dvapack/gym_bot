from typing import List, Dict
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# TODO добавить логгер
def get_main_keyboard():
    """
    Основная клавиатура

    Returns:
        InlineKeyboardMarkup: Клавиатуру с кнопками: новая тренировка и мои тренировки
    """
    keyboard = [
        [
            InlineKeyboardButton(text="Новая тренировка", callback_data="new_workout"),
            InlineKeyboardButton(text="Мои тренировки", callback_data="my_workouts")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# TODO пересмотреть кнопки
# TODO добавить логгер
def start_workout_keyboard(muscle_groups: List[str]):
    """
    Клавиатура для новой тренировки

    Args:
        muscle_groups (List[str]): Мышечные группы

    Returns:
        InlineKeyboardMarkup: Клавиатуру с выбором мышечной группы или добавлением новой
    """
    keyboard = []
    for muscle_group in muscle_groups:
        keyboard.append([InlineKeyboardButton(text=muscle_group, callback_data=f"select_muscle_group:{muscle_group}")])
    keyboard.append([InlineKeyboardButton(text="Новая группа мышц", callback_data="new_muscle_group")])
    keyboard.append([InlineKeyboardButton(text="Завершить тренировку", callback_data="finish_workout")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# TODO добавить docstring
# TODO добавить логгер
def get_exercise_keyboard(exercises: List[str]):
    """
    Клавиатура для выбора упражнения
    """
    keyboard = []
    for exercise in exercises:
        keyboard.append([InlineKeyboardButton(text=exercise, callback_data="select_exercise")])
    keyboard.append([InlineKeyboardButton(text="Новое упражнение", callback_data="new_exercise")])
    keyboard.append([InlineKeyboardButton(text="Завершить тренировку", callback_data="finish_workout")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# TODO добавить docstring
# TODO добавить логгер
def get_back_keyboard():
    """
    Клавиатура с кнопкой Назад
    """
    keyboard = [[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
