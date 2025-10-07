from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from bot.keyboard.keyboard import get_main_keyboard, start_workout_keyboard
from database.database import Database

db: Database = None

router = Router()
user_id = None

# TODO добавить docstring
@router.callback_query(F.data == "new_workout")
async def create_new_workout(callback: CallbackQuery):
    """
    Хендлер нажатия на кнопку "Новая тренировка"
    """
    if db is None or db.pool is None:
        await callback.message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.message.from_user
    workout_id = await db.create_workout(user.id)

    text = f"""
    Привет, {user.first_name}!

Я твой персональный фитнес-трекер!

Выбери действие ниже или используй команды:
/new_workout - Начать новую тренировку
/my_workouts - Мои последние тренировки
    """
    await callback.message.answer(
        text,
        reply_markup=start_workout_keyboard()
    )

