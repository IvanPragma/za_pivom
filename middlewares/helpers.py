from aiogram import Bot
from aiogram.types import Message
from conf import LOGGING_SUPERGROUP_ID
from database.base import get_session
from database.models import User
from loguru import logger


async def forward_bot_message_to_user_topic(bot: Bot, sent_message: Message, user_tg_id: int) -> None:
    """Forward a bot-sent message from a private chat to the user's topic in the supergroup.

    Only forwards if the message chat is private and the user has a topic.
    """
    try:
        if getattr(sent_message.chat, "type", None) != "private":
            return

        session = await get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.tg_id == user_tg_id))
            user = result.scalar_one_or_none()
        finally:
            await session.close()

        if not user or not user.topic_id:
            return

        await bot.forward_message(
            chat_id=LOGGING_SUPERGROUP_ID,
            from_chat_id=sent_message.chat.id,
            message_id=sent_message.message_id,
            message_thread_id=user.topic_id,
        )
    except Exception as e:
        logger.error(f"Ошибка пересылки сообщения бота для пользователя {user_tg_id}: {e}")


async def send_referral_notification(bot: Bot, referrer_user: User, new_user: User) -> None:
    """Отправляет уведомление в тему реферера о новом реферале"""
    try:
        if not referrer_user.topic_id:
            return
            
        # Формируем имя нового пользователя
        new_user_name = f"{new_user.first_name or ''} {new_user.last_name or ''}".strip()
        if not new_user_name:
            new_user_name = f"@{new_user.username}" if new_user.username else f"ID: {new_user.tg_id}"
        
        # Формируем сообщение
        notification_text = f"🎁 <b>Новый реферал!</b>\n\nПрисоединился: {new_user_name}"
        
        # Если у нового пользователя есть тема, добавляем ссылку
        if new_user.topic_id:
            # Создаем ссылку на тему нового пользователя
            topic_link = f"https://t.me/c/{str(LOGGING_SUPERGROUP_ID)[4:]}/{new_user.topic_id}"
            notification_text += f"\n\n🔗 <a href=\"{topic_link}\">Перейти к теме реферала</a>"
        
        await bot.send_message(
            chat_id=LOGGING_SUPERGROUP_ID,
            text=notification_text,
            message_thread_id=referrer_user.topic_id,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о реферале для пользователя {referrer_user.tg_id}: {e}")


