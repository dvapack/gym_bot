from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.database import Database

from datetime import datetime
import logging

from bot.FSM.fsm_states import States, load_muscle_groups, load_exercises
from bot.keyboard.keyboard import start_workout_keyboard, get_exercise_keyboard, get_back_to_exercises, \
                                    get_main_keyboard, get_last_workouts_keyboard, back_from_workout_view


db: Database = None

router = Router()

logger = logging.getLogger(__name__)

###########################
# Flow загрузки данных
###########################
@router.callback_query(
        States.start,
        F.data == "import_data")
async def import_data(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку "Импорт данных"

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с инструкцией по импорту данных
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    logger.info("Пользователь %s начал импорт данных", user.id)

    text = f"""
Вы выбрали импорт данных.
Пожалуйста, отправьте CSV файл с вашими тренировками в следующем формате:
Date	Exercise	Category	Weight	Weight Unit	Reps
Пример:
2024-01-01, Жим лежа, Грудь, 80, kgs, 10
2024-01-01, Жим лежа, Грудь, 85, kgs, 8
После отправки файла, ваши данные будут обработаны и добавлены в базу данных.
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_main_keyboard()
    )
    await state.set_state(States.import_data)

###########################
# Flow заполнения тренировки
###########################
@router.callback_query(
        States.start,
        F.data == "new_workout")
async def create_new_workout(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку "Новая тренировка"

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    logger.info("Пользователь %s начал новую тренировку", user.id)
    workout_id = await db.create_workout(user.id)

    await state.update_data(workout_id=workout_id)
    muscle_groups = await load_muscle_groups(user.id)

    text = f"""
    Вы начали тренировку.
Выберите группу мышц:
    """
    await callback.message.edit_text(
        text,
        reply_markup=start_workout_keyboard(muscle_groups)
    )
    await state.set_state(States.choosing_muscle_group)

@router.callback_query(
        States.choosing_muscle_group,
        F.data.startswith("select_muscle_group"))
async def select_muscle_group(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку с конкретной группой мышц

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    muscle_group = callback.data.split(":")[1]
    await state.update_data(muscle_group=muscle_group)
    exersices = await load_exercises(user.id, muscle_group)
    await state.update_data(set_order={})
    text = f"""
    Вы выбрали {muscle_group}.
Выберите упражнение:
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_exercise_keyboard(exersices)
    )
    await state.set_state(States.choosing_exercise)

@router.callback_query(
        States.choosing_exercise,
        F.data == "new_exercise")
async def add_exercise(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку "Новое упражнение"

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Текст с инструкцией по добавлению нового упражнения
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    logger.info("Пользователь %s начал новую тренировку", user.id)
    text = f"""
    Чтобы добавить новое упражнение, пожалуйста, введите его название и группу мышц в формате:
Название упражнения
Пример:
Жим гантелей
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_exercises()
    )
    await state.set_state(States.adding_exercise)

@router.callback_query(
        States.choosing_muscle_group,
        F.data.startswith("select_muscle_group"))
async def select_muscle_group(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку с конкретной группой мышц

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    muscle_group = callback.data.split(":")[1]
    await state.update_data(muscle_group=muscle_group)
    exersices = await load_exercises(user.id, muscle_group)
    await state.update_data(set_order={})
    text = f"""
    Вы выбрали {muscle_group}.
Выберите упражнение:
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_exercise_keyboard(exersices)
    )
    await state.set_state(States.choosing_exercise)
    

@router.callback_query(
        States.choosing_exercise,
        F.data.startswith("select_exercise"))
async def select_exercise(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку с конкретным упражнением

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    exercise = callback.data.split(":")[1]
    exercise_id = await db.get_exercise_by_name(exercise, user.id)
    data_updates = {
        'exercise': exercise,
        'exercise_id': exercise_id
    }
    await state.update_data(**data_updates)
    text = f"""
    Вы выбрали {exercise}.
Введите количество килограм и повторений
(например, 20 10):
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_exercises()
    )
    await state.set_state(States.entering_set_info)

@router.callback_query(
        StateFilter(States.entering_set_info, States.adding_exercise),
        F.data == "back_to_exercise")
async def back_to_choosing_exercise(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку назад при вводе данных о подходе

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    user_data = await state.get_data()
    muscle_group = user_data['muscle_group']
    exersices = await load_exercises(user.id, muscle_group)
    text = f"""
    Вы выбрали {muscle_group}.
Выберите упражнение:
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_exercise_keyboard(exersices)
    )
    await state.set_state(States.choosing_exercise)

@router.callback_query(
        States.choosing_exercise,
        F.data == "back_to_muscle_group")
async def back_to_choosing_muscle_group(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку назад при выборе упражнения

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    muscle_groups = await load_muscle_groups(user.id)

    text = f"""
Выберите группу мышц:
    """
    await callback.message.edit_text(
        text,
        reply_markup=start_workout_keyboard(muscle_groups)
    )
    await state.set_state(States.choosing_muscle_group)

@router.callback_query(F.data == 'finish_workout')
async def finish_workout(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку завершения тренировки

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    await state.set_data({})
    text = f"""
Тренировка завершена!

Выбери действие ниже или используй команды:
/new_workout - Начать новую тренировку
/my_workouts - Мои последние тренировки
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_main_keyboard()
    )
    await state.set_state(States.start)


###########################
# Flow просмотра тренировок
###########################
@router.callback_query(
        StateFilter(States.start, States.view_workouts),
        F.data == 'my_workouts')
async def view_workouts(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку мои последние тренировки

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    await state.set_data({})
    user = callback.from_user
    dates = await db.get_workout_dates(telegram_id=user.id)
    text = f"""
Выберите тренировку:
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_last_workouts_keyboard(dates)
    )
    await state.set_state(States.view_workouts)

@router.callback_query(
        States.view_workouts,
        F.data.startswith("get_workout"))
async def select_workout(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку с конкретной тренировкой

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    user = callback.from_user
    date = callback.data.split(":")[1]
    date = datetime.strptime(date, "%Y-%m-%d")
    workout = await db.get_workout_by_date(telegram_id=user.id, date=date)
    text = f"""
Тренировка {str(date)}:
"""
    for item in workout:
        text += f"{item['name']} - Подход: {item['set_order']} - {item['weight']}кг × {item['reps']} повторений\n"
    await callback.message.edit_text(
        text,
        reply_markup=back_from_workout_view()
    )
    await state.set_state(States.view_workouts)

@router.callback_query(
        StateFilter(States.view_workouts, States.view_workouts),
        F.data == 'back_to_main')
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер нажатия на кнопку назад при просмотре тренировок

    Args:
        callback (CallbackQuery): кнопка, на которую нажал пользователь
        state (FSMContext): состояние, в котором находится пользователь

    Returns:
        Новое сообщение с клавиатурой
    """
    if db is None or db.pool is None:
        logger.warning("База данных не инициализирована")
        await callback.message.edit_text("Бот инициализируется, попробуйте через несколько секунд...")
        return
    await state.set_data({})
    text = f"""
Выбери действие ниже или используй команды:
/new_workout - Начать новую тренировку
/my_workouts - Мои последние тренировки
    """
    await callback.message.edit_text(
        text,
        reply_markup=get_main_keyboard()
    )
    await state.set_state(States.start)