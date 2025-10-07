from typing import List, Dict
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    """
    Основная клавиатура
    """
    keyboard = [
        [
            InlineKeyboardButton(text="Новая тренировка", callback_data="new_workout"),
            InlineKeyboardButton(text="Мои тренировки", callback_data="my_workouts")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def start_workout_keyboard():
    """
    Клавиатура для новой тренировки
    """
    keyboard = [
        [
            InlineKeyboardButton(text="Группа мышц", callback_data="get_muscle_groups"),
            InlineKeyboardButton(text="Новая группа мышц", callback_data="new_muscle_group")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

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

def get_back_keyboard():
    """
    Клавиатура с кнопкой Назад
    """
    keyboard = [[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
