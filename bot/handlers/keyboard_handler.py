from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from bot.keyboard.keyboard import get_main_keyboard
from database.database import Database

db: Database = None

router = Router()
user_id = None

@router.callback_query(F.data == "new_workout")
async def create_new_workout(callback: CallbackQuery):
    """
    Хендлер нажатия на кнопку "Новая тренировка"
    """
    if db is None or db.pool is None:
        await message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = message.from_user
    user_id = await db.get_create_user(user.id)

    text = f"""
    Привет, {user.first_name}!

Я твой персональный фитнес-трекер!

Выбери действие ниже или используй команды:
/new_workout - Начать новую тренировку
/my_workouts - Мои последние тренировки
    """
    await message.answer(
        text,
        reply_markup=get_main_keyboard()
    )

