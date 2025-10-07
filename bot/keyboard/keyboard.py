from typing import List, Dict
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
def start_workout_keyboard(muscle_groups: List[str] = None):
    """
    Клавиатура для новой тренировки

    Args:
        muscle_groups (List[str]): Мышечные группы

    Returns:
        InlineKeyboardMarkup: Клавиатуру с выбором мышечной группы или добавлением новой
    """
    keyboard = []
    for muscle_group in muscle_groups:
        keyboard.append([InlineKeyboardButton(text=muscle_group, callback_data="select_muscle_group")])
    keyboard.append([InlineKeyboardButton(text="Новое упражнение", callback_data="new_exersice")])
    keyboard.append([InlineKeyboardButton(text="Завершить тренировку", callback_data="finish_workout")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# TODO добавить docstring
def get_exercise_keyboard(exercises: List[Dict]):
    """
    Клавиатура для выбора упражнения
    """
    keyboard = []
    for exercise in exercises:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{exercise['name']} ({exercise['muscle_group']})",
                callback_data=f"ex_{exercise['name']}_{exercise['muscle_group']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="Новое упражнение", callback_data="new_exersice")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# TODO добавить docstring
def get_back_keyboard():
    """
    Клавиатура с кнопкой Назад
    """
    keyboard = [[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
