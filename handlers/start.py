from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.inline import get_main_menu, get_admin_menu
from conf import ADMIN_IDS
from middlewares.helpers import forward_bot_message_to_user_topic

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    places_text = "🔥 Последние места на доп. набор!"
    
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
    places_text = "🔥 Последние места на доп. набор!"
    
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
