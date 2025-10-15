from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.database import Database

from bot.keyboard.keyboard import get_main_keyboard, get_back_keyboard
from bot.FSM.fsm_states import States

import logging

db: Database = None

logger = logging.getLogger(__name__)

router = Router()

@router.message(StateFilter(None), Command("start"))
async def command_start(message: Message, state: FSMContext):
    """
    Хендлер команды /start

    Args:
        message (Message): сообщение пользователя
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = message.from_user
    logger.info("Получена /start команда от user_id=%s", user.id)
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


@router.message(States.entering_set_info)
async def enter_set_information(message: Message, state: FSMContext):
    """
    Хендлер ввода данных о первом подходе
    
    Args:
        message (Message): сообщение пользователя
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = message.from_user
    ## TODO обернуть в трайкетч и добавить валидацию
    user_data = await state.get_data()
    workout_id = user_data.get("workout_id")
    exercise_id = user_data.get("exercise_id")
    exercise = user_data.get("exercise")
    set_order = user_data['set_order'].get(exercise, 0) + 1
    weight, reps = (int(number) for number in message.text.split())
    logger.debug("Добавление подхода: workout_id=%s, exercise_id=%s, set_order=%s, weight=%s, reps=%s",
                 workout_id, exercise_id, set_order, weight, reps)
    await db.add_set_to_workout(workout_id, exercise_id, set_order, weight, reps)
    data_updates = {
        'exercise': exercise,
        'exercise_id': exercise_id,
        'set_order': {**user_data['set_order'], exercise: set_order} 
    }
    await state.update_data(**data_updates)
    sets = await db.get_workout_sets_by_exercise(exercise_id, workout_id)
    text = """
Данные записаны!                  
Текущие подходы:                   
"""
    for item in sets:
        text += f"{item['set_order']}: {item['weight']}кг × {item['reps']} повторений\n"
    await message.answer(
        text,
        reply_markup=get_back_keyboard('exercise')
    )
    await state.set_state(States.entering_set_info)
