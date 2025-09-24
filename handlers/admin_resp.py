from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from conf import LOGGING_SUPERGROUP_ID, ADMIN_IDS
from database.base import get_session
from database.models import User
from sqlalchemy import select
from loguru import logger

router = Router()


@router.message(Command("resp"))
async def admin_response(message: Message):
    """Команда /resp для ответа пользователю в теме"""
    # Проверяем, что это сообщение в супергруппе от администратора
    if (message.chat.id != LOGGING_SUPERGROUP_ID or 
        not message.message_thread_id or 
        not message.from_user or 
        message.from_user.id not in ADMIN_IDS):
        return
    
    # Получаем текст ответа (убираем "/resp")
    response_text = message.text[5:].strip()  # Убираем "/resp " (5 символов)
    
    if not response_text:
        await message.reply("Использование: /resp <текст ответа>")
        return
    
    # Находим пользователя по topic_id
    session = await get_session()
    try:
        result = await session.execute(
            select(User).where(User.topic_id == message.message_thread_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.reply("Пользователь с такой темой не найден")
            return
        
        # Отправляем ответ пользователю
        await message.bot.send_message(
            chat_id=user.tg_id,
            text=response_text
        )
        
        # Подтверждаем администратору
        await message.reply(f"✅ Ответ отправлен пользователю {user.tg_id}")
        
        logger.info(f"Ответ от админа {message.from_user.id} отправлен пользователю {user.tg_id}: {response_text}")
        
    except Exception as e:
        logger.error(f"Ошибка отправки ответа пользователю: {e}")
        await message.reply("❌ Ошибка отправки ответа")
    finally:
        await session.close()
