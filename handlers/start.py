from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.inline import get_main_menu, get_admin_menu
from conf import ADMIN_IDS
from middlewares.helpers import forward_bot_message_to_user_topic
from utils.config import get_remaining_places, get_max_places
from database.base import get_session
from database.models import User, Payment
from sqlalchemy import select, func

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    # Получаем количество пользователей с подпиской
    session = await get_session()
    try:
        # Считаем уникальные подписки (не платежи)
        users_with_subscription = await session.scalar(
            select(func.count(func.distinct(User.id)))
            .select_from(User)
            .join(Payment, User.id == Payment.user_id)
            .where(Payment.status == "paid")
        ) or 0
        
        # Получаем оставшиеся места
        remaining_places = get_remaining_places() - users_with_subscription
        
        # Формируем текст с счетчиком мест
        # Получаем максимальное количество мест из конфига
        max_places = get_max_places()
        places_text = f"🔥 Осталось мест: {remaining_places}/{max_places}"
        if remaining_places <= 5:
            places_text += " ⚠️"
        elif remaining_places <= 10:
            places_text += " ⚡"
            
    finally:
        await session.close()
    
    welcome_text = (
        f"{places_text}\n\n"
        "Привет 👋\n\n"
        "Это официальный бот сервиса, который помогает студентам закрыть физру без нервов и потери времени.\n"
        "Мы гарантируем, что студент наберет 100 баллов с нами при минимальных усилиях."
    )
    
    # Проверяем, является ли пользователь админом
    if message.from_user.id in ADMIN_IDS:
        keyboard = get_admin_menu()
    else:
        keyboard = get_main_menu()
    
    sent = await message.answer(welcome_text, reply_markup=keyboard)
    # Перешлём ответ бота в тему пользователя (только в ЛС)
    await forward_bot_message_to_user_topic(message.bot, sent, message.from_user.id)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    # Получаем количество пользователей с подпиской
    session = await get_session()
    try:
        # Считаем уникальные подписки (не платежи)
        users_with_subscription = await session.scalar(
            select(func.count(func.distinct(User.id)))
            .select_from(User)
            .join(Payment, User.id == Payment.user_id)
            .where(Payment.status == "paid")
        ) or 0
        
        # Получаем оставшиеся места
        remaining_places = get_remaining_places() - users_with_subscription
        
        # Формируем текст с счетчиком мест
        # Получаем максимальное количество мест из конфига
        max_places = get_max_places()
        places_text = f"🔥 Осталось мест: {remaining_places}/{max_places}"
        if remaining_places <= 5:
            places_text += " ⚠️"
        elif remaining_places <= 10:
            places_text += " ⚡"
            
    finally:
        await session.close()
    
    welcome_text = (
        f"{places_text}\n\n"
        "Привет 👋\n\n"
        "Это официальный бот сервиса, который помогает студентам закрыть физру без нервов и потери времени.\n"
        "Мы гарантируем, что студент наберет 100 баллов с нами при минимальных усилиях."
    )
    
    # Проверяем, является ли пользователь админом
    if callback.from_user.id in ADMIN_IDS:
        keyboard = get_admin_menu()
    else:
        keyboard = get_main_menu()
    
    await callback.message.edit_text(welcome_text, reply_markup=keyboard)
    await callback.answer()
