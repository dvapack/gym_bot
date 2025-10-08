from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from bot.keyboard.keyboard import get_main_keyboard
from database.database import Database
from bot.FSM.fsm_states import States
from aiogram.fsm.context import FSMContext

db: Database = None

router = Router()
user_id = None

# TODO добавить docstring
# TODO добавить логгер
@router.message(StateFilter(None), Command("start"))
async def command_start(message: Message, state: FSMContext):
    """
    Хендлер команды /start
    """
    if db is None or db.pool is None:
        await message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = message.from_user
    user_id = await db.get_create_user(user.id)
    await db._fill_exercises(user.id)

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
    await state.set_state(States.start)

# TODO добавить docstring
# TODO добавить логгер
@router.message(States.entering_set_info)
async def select_exercise(message: Message, state: FSMContext):
    """
    Хендлер нажатия на кнопку с конкретным упражнением
    """
    if db is None or db.pool is None:
        await message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = message.from_user
    ## TODO обернуть в трайкетч и добавить валидацию
    weight, reps = (int(number) for number in message.text.split())

    text = f"""
    Вы выбрали {exercise}.
Введите количество килограм и повторений
(например, 20 10):
    """
    await callback.message.answer(
        text,
        reply_markup=get_back_keyboard()
    )
    await state.set_state(States.entering_set_info)