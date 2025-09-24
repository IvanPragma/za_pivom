from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from conf import LOGGING_SUPERGROUP_ID
from database.base import get_session
from database.models import User
from loguru import logger
from middlewares.helpers import send_referral_notification
from utils.referral import get_unique_referral_code, get_user_by_referral_code


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Обрабатываем сообщения и callback'и из личных чатов
        if isinstance(event, (Message, CallbackQuery)):
            # Пересылаем только если это личный чат с ботом
            chat = event.chat if isinstance(event, Message) else event.message.chat
            if getattr(chat, "type", None) != "private":
                return await handler(event, data)
            try:
                user_id = event.from_user.id
                username = event.from_user.username
                first_name = event.from_user.first_name
                
                # Получаем или создаем пользователя
                session = await get_session()
                try:
                    # Ищем пользователя по tg_id, а не по id
                    from sqlalchemy import select
                    result = await session.execute(select(User).where(User.tg_id == user_id))
                    user = result.scalar_one_or_none()
                    
                    if not user:
                        # Получаем реферальную информацию и UTM метки из команды /start
                        referrer_id = None
                        utm_source = None
                        if isinstance(event, Message) and event.text and event.text.startswith('/start'):
                            parts = event.text.split()
                            if len(parts) > 1:
                                start_param = parts[1]
                                
                                # Проверяем реферальную ссылку
                                if start_param.startswith('ref'):
                                    try:
                                        referral_code = start_param[3:]  # Убираем "ref" и получаем реферальный код
                                        # Проверяем, существует ли реферер в базе данных
                                        referrer_user = await get_user_by_referral_code(referral_code)
                                        if referrer_user:
                                            referrer_id = referrer_user.id
                                    except Exception:
                                        pass  # Неверный формат, игнорируем
                                
                                # Проверяем UTM метки
                                elif start_param.startswith('utm'):
                                    utm_source = start_param[3:]  # Убираем "utm" и получаем UTM метку
                        
                        # Создаем нового пользователя
                        referral_code = await get_unique_referral_code()
                        user = User(
                            tg_id=user_id,
                            username=username,
                            first_name=first_name,
                            last_name=event.from_user.last_name,
                            referrer_id=referrer_id,
                            referral_code=referral_code,
                            utm_source=utm_source
                        )
                        session.add(user)
                        await session.commit()
                    else:
                        # Обновляем данные пользователя если изменились
                        if (user.username != username or 
                            user.first_name != first_name or 
                            user.last_name != event.from_user.last_name):
                            user.username = username
                            user.first_name = first_name
                            user.last_name = event.from_user.last_name
                            await session.commit()
                            
                            # Обновляем закрепленное сообщение
                            await self._update_user_pinned_message(event, user)
                    
                    # Пересылаем сообщение в тему пользователя
                    await self._forward_to_user_topic(event, user)
                finally:
                    await session.close()
            except Exception as e:
                logger.error(f"Ошибка в LoggingMiddleware: {e}")
        
        return await handler(event, data)
    
    async def _create_user_topic(self, event: TelegramObject, user: User) -> None:
        """Создает тему для пользователя в супергруппе"""
        try:
            bot = event.bot
            # Создаем тему
            topic_name = f"@{user.username}" if user.username else f"ID: {user.tg_id}"
            topic = await bot.create_forum_topic(
                chat_id=LOGGING_SUPERGROUP_ID,
                name=topic_name
            )
            
            # Отправляем и закрепляем сообщение с данными пользователя (plain text)
            user_info = (
                f"ID: {user.tg_id}\n"
                f"Username: @{user.username or 'Нет'}\n"
                f"Имя: {user.first_name or 'отсутствует'} {user.last_name or ''}"
            )
            
            # Добавляем UTM метку, если есть
            if user.utm_source:
                user_info += f"\n📊 UTM: {user.utm_source}"
            
            # Добавляем информацию о реферере, если есть
            if user.referrer_id:
                session = await get_session()
                try:
                    from sqlalchemy import select
                    referrer_result = await session.execute(select(User).where(User.id == user.referrer_id))
                    referrer = referrer_result.scalar_one_or_none()
                    if referrer:
                        referrer_name = f"{referrer.first_name or ''} {referrer.last_name or ''}".strip()
                        if not referrer_name:
                            referrer_name = f"@{referrer.username}" if referrer.username else f"ID: {referrer.tg_id}"
                        user_info += f"\n\n🎁 Пришел по реферальной ссылке от: {referrer_name}"
                finally:
                    await session.close()
            
            message = await bot.send_message(
                chat_id=LOGGING_SUPERGROUP_ID,
                text=user_info,
                message_thread_id=topic.message_thread_id
            )
            
            # Закрепляем сообщение
            await bot.pin_chat_message(
                chat_id=LOGGING_SUPERGROUP_ID,
                message_id=message.message_id
            )
            
            # Сохраняем ID темы и закрепленного сообщения в пользователе
            session = await get_session()
            try:
                # Обновляем пользователя в БД
                from sqlalchemy import update
                await session.execute(
                    update(User)
                    .where(User.tg_id == user.tg_id)
                    .values(
                        topic_id=topic.message_thread_id,
                        pinned_message_id=message.message_id
                    )
                )
                await session.commit()
                
                # Обновляем переданный объект пользователя в памяти
                user.topic_id = topic.message_thread_id
                user.pinned_message_id = message.message_id
            finally:
                await session.close()
            
        except Exception as e:
            logger.error(f"Ошибка создания темы для пользователя {user.tg_id}: {e}")
    
    async def _update_user_pinned_message(self, event: TelegramObject, user: User) -> None:
        """Обновляет закрепленное сообщение пользователя"""
        try:
            if not user.topic_id or not user.pinned_message_id:
                return
                
            bot = event.bot
            
            # Обновляем информацию о пользователе (plain text)
            user_info = (
                f"ID: {user.tg_id}\n"
                f"Username: @{user.username or 'Нет'}\n"
                f"Имя: {user.first_name or 'отсутствует'} {user.last_name or ''}"
            )
            
            # Добавляем UTM метку, если есть
            if user.utm_source:
                user_info += f"\n📊 UTM: {user.utm_source}"
            
            # Добавляем информацию о реферере, если есть
            if user.referrer_id:
                session = await get_session()
                try:
                    from sqlalchemy import select
                    referrer_result = await session.execute(select(User).where(User.id == user.referrer_id))
                    referrer = referrer_result.scalar_one_or_none()
                    if referrer:
                        referrer_name = f"{referrer.first_name or ''} {referrer.last_name or ''}".strip()
                        if not referrer_name:
                            referrer_name = f"@{referrer.username}" if referrer.username else f"ID: {referrer.tg_id}"
                        user_info += f"\n\n🎁 Пришел по реферальной ссылке от: {referrer_name}"
                finally:
                    await session.close()
            
            await bot.edit_message_text(
                chat_id=LOGGING_SUPERGROUP_ID,
                message_id=user.pinned_message_id,
                text=user_info
            )
            
        except Exception as e:
            logger.error(f"Ошибка обновления закрепленного сообщения для пользователя {user.tg_id}: {e}")
    
    async def _forward_to_user_topic(self, event: TelegramObject, user: User) -> None:
        """Пересылает сообщение в тему пользователя"""
        try:
            bot = event.bot
            
            # Если у пользователя нет темы, создаем её и продолжаем
            if not user.topic_id:
                await self._create_user_topic(event, user)
                # После создания темы нужно перезагрузить пользователя из БД
                session = await get_session()
                try:
                    from sqlalchemy import select
                    result = await session.execute(select(User).where(User.tg_id == user.tg_id))
                    user = result.scalar_one()
                    
                    # Отправляем уведомление рефереру, если есть
                    if user.referrer_id:
                        referrer_result = await session.execute(select(User).where(User.id == user.referrer_id))
                        referrer_user = referrer_result.scalar_one_or_none()
                        if referrer_user:
                            await send_referral_notification(event.bot, referrer_user, user)
                finally:
                    await session.close()
            
            if user.topic_id:
                if isinstance(event, Message):
                    # Пересылаем сообщение в тему пользователя
                    await bot.forward_message(
                        chat_id=LOGGING_SUPERGROUP_ID,
                        from_chat_id=event.chat.id,
                        message_id=event.message_id,
                        message_thread_id=user.topic_id
                    )
                elif isinstance(event, CallbackQuery):
                    # Отправляем информацию о callback'е
                    callback_text = f"<кликнул \"{event.data}\">"
                    await bot.send_message(
                        chat_id=LOGGING_SUPERGROUP_ID,
                        text=callback_text,
                        message_thread_id=user.topic_id
                    )
                
        except Exception as e:
            logger.error(f"Ошибка пересылки сообщения от пользователя {user.tg_id}: {e}")
