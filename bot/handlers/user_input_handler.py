from aiogram import F, Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ContentType
from aiogram.fsm.context import FSMContext

import tempfile

from database.database import Database

from bot.keyboard.keyboard import get_main_keyboard, get_back_to_exercises
from bot.FSM.fsm_states import States
from dataloader.dataloader import Dataloader

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
        reply_markup=get_back_to_exercises()
    )
    await state.set_state(States.entering_set_info)

@router.message(States.adding_exercise)
async def enter_exrcise_information(message: Message, state: FSMContext):
    """
    Хендлер ввода данных о новом упражнении
    
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
    user_data = await state.get_data()
    exercise = message.text
    muscle_group = user_data.get("muscle_group")
    logger.debug("Добавление упражнения: user_id=%s, muscle_group=%s, exercise=%s",
                 user.id, muscle_group, exercise)
    exercise_id = await db.create_exercise(telegram_id=user.id, muscle_group=muscle_group, name=exercise)
    data_updates = {
        'exercise': exercise,
        'exercise_id': exercise_id
    }
    await state.update_data(**data_updates)
    text = """
Упражнение добавлено!                  
Введите первый подход в формате:
Вес Повторения
Пример:
80 10                 
"""
    await message.answer(
        text,
        reply_markup=get_back_to_exercises()
    )
    await state.set_state(States.entering_set_info)

@router.message(States.import_data,
                F.content_type == ContentType.DOCUMENT)
async def import_data_handler(message: Message, state: FSMContext):
    """
    Хендлер для обработки импорта данных из CSV файла

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
    document = message.document
    
    if not document.file_name.endswith('.csv'):
        await message.answer("Пожалуйста, отправьте файл в формате CSV.")
        return
    file = await message.bot.get_file(document.file_id)
    file_path = file.file_path
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
            await message.bot.download_file(file_path, temp_file.name)
            dataloader = Dataloader(temp_file.name)
            dataloader.set_order()
            dataloader.filter_data()
            muscle_groups = dataloader.get_muscle_groups()
            exercise_ids = {}
            for muscle_group in muscle_groups:
                exercises = dataloader.get_exercises_by_muscle_group(muscle_group)
                for exercise in exercises:
                    exercise_id = await db.create_exercise(telegram_id=user.id, muscle_group=muscle_group, name=exercise)
                    if exercise not in exercise_ids:
                        exercise_ids[exercise] = exercise_id
            workouts = dataloader.get_workouts()
            for workout_date, workout_data in workouts.items():
                workout_id = await db.import_workout(telegram_id=user.id, date=workout_date)
                for set_info in workout_data['sets']:
                    exercise_id = exercise_ids.get(set_info['exercise'])
                    await db.add_set_to_workout(
                        workout_id=workout_id,
                        exercise_id=exercise_id,
                        set_order=set_info['set_number'],
                        weight=set_info['weight'],
                        reps=set_info['reps']
                    )
    text = "Данные успешно импортированы!"
    await message.answer(
        text,
        reply_markup=get_main_keyboard()
    )
    await state.set_state(States.start)

