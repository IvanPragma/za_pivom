from aiogram import Router, F
from aiogram.types import Message
from middlewares.helpers import forward_bot_message_to_user_topic

router = Router()


@router.message(F.chat.type == "private")
async def handle_all_private_messages(message: Message):
    """Обрабатывает все сообщения в личных чатах"""
    # Этот хендлер срабатывает для всех сообщений в ЛС
    # Middleware уже обработал пересылку сообщения пользователя
    # Здесь мы можем добавить дополнительную логику если нужно
    pass
