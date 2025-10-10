from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from bot.FSM.fsm_states import States, load_muscle_groups, load_exercises
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.keyboard.keyboard import start_workout_keyboard, get_exercise_keyboard, get_back_keyboard
from database.database import Database

db: Database = None

router = Router()
user_id = None

# TODO добавить docstring
# TODO добавить логгер
@router.callback_query(
        States.start,
        F.data == "new_workout")
async def create_new_workout(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку "Новая тренировка"
    """
    if db is None or db.pool is None:
        await callback.message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    workout_id = await db.create_workout(user.id)

    await state.update_data(workout_id=workout_id)
    muscle_groups = await load_muscle_groups(user.id)

    text = f"""
    Вы начали тренировку.
Выберите группу мышц:
    """
    await callback.message.answer(
        text,
        reply_markup=start_workout_keyboard(muscle_groups)
    )
    await state.set_state(States.choosing_muscle_group)

# TODO добавить docstring
# TODO добавить логгер
@router.callback_query(
        States.choosing_muscle_group,
        F.data.startswith("select_muscle_group"))
async def select_muscle_group(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку с конкретной группой мышц
    """
    if db is None or db.pool is None:
        await callback.message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    muscle_group = callback.data.split(":")[1]

    exersices = await load_exercises(user.id, muscle_group)
    await state.update_data(set_order={})
    text = f"""
    Вы выбрали {muscle_group}.
Выберите упражнение:
    """
    await callback.message.answer(
        text,
        reply_markup=get_exercise_keyboard(exersices)
    )
    await state.set_state(States.choosing_exercise)

# TODO добавить docstring
# TODO добавить логгер
@router.callback_query(
        States.choosing_exercise,
        F.data.startswith("select_exercise"))
async def select_exercise(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку с конкретным упражнением
    """
    if db is None or db.pool is None:
        await callback.message.answer("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    exercise = callback.data.split(":")[1]
    exercise_id = await db.get_exercise_by_name(exercise, user.id)
    user_data = await state.get_data()
    current_set_order = user_data['set_order'].get(exercise, 0) + 1
    data_updates = {
        'exercise': exercise,
        'exercise_id': exercise_id,
        'set_order': {**user_data['set_order'], exercise: current_set_order}
    }
    await state.update_data(**data_updates)
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

