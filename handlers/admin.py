from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import get_admin_menu, get_main_menu
from conf import ADMIN_IDS
from database.base import get_session
from database.models import User
from sqlalchemy import select, func
from loguru import logger

router = Router()


class BroadcastStates(StatesGroup):
    waiting_for_message = State()


def admin_check(func):
    """Декоратор для проверки прав администратора"""
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("У вас нет прав для выполнения этого действия", show_alert=True)
            return
        # Убираем лишние аргументы, которые может передавать aiogram
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in func.__code__.co_varnames}
        return await func(callback, *args, **filtered_kwargs)
    return wrapper


@router.callback_query(F.data == "admin_stats")
@admin_check
async def show_stats(callback: CallbackQuery):
    """Показывает статистику пользователей"""
    try:
        session = await get_session()
        try:
            # Общее количество пользователей
            total_users = await session.scalar(select(func.count(User.id)))
            
            # Пользователи за последние 7 дней
            from datetime import datetime, timedelta, timezone
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            new_users_week = await session.scalar(
                select(func.count(User.id)).where(User.created_at >= week_ago)
            )
            
            # Пользователи за последние 30 дней
            month_ago = datetime.now(timezone.utc) - timedelta(days=30)
            new_users_month = await session.scalar(
                select(func.count(User.id)).where(User.created_at >= month_ago)
            )
            
            stats_text = (
                "📊 **Статистика пользователей**\n\n"
                f"👥 **Всего пользователей:** {total_users}\n"
                f"📈 **За последние 7 дней:** {new_users_week}\n"
                f"📈 **За последние 30 дней:** {new_users_month}\n\n"
                "Для массовой рассылки нажмите '📢 Массовая рассылка'"
            )
            
            await callback.message.edit_text(
                stats_text,
                reply_markup=get_admin_menu(),
                parse_mode="Markdown"
            )
        finally:
            await session.close()
            
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await callback.answer("Ошибка при получении статистики", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
@admin_check
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс массовой рассылки"""
    await state.set_state(BroadcastStates.waiting_for_message)
    
    broadcast_text = (
        "📢 **Массовая рассылка**\n\n"
        "Отправьте сообщение, которое будет разослано всем пользователям бота.\n\n"
        "Поддерживаются:\n"
        "• Текст\n"
        "• Фото с подписью\n"
        "• Документы\n\n"
        "Для отмены отправьте /cancel"
    )
    
    await callback.message.edit_text(
        broadcast_text,
        reply_markup=get_admin_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(BroadcastStates.waiting_for_message)
@admin_check
async def process_broadcast_message(message: Message, state: FSMContext):
    """Обрабатывает сообщение для рассылки"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Рассылка отменена", reply_markup=get_admin_menu())
        return
    
    try:
        # Получаем всех пользователей
        session = await get_session()
        try:
            users = await session.scalars(select(User.tg_id))
            user_ids = [user for user in users]
        finally:
            await session.close()
        
        if not user_ids:
            await message.answer("Нет пользователей для рассылки", reply_markup=get_admin_menu())
            await state.clear()
            return
        
        # Отправляем сообщение всем пользователям
        success_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            try:
                if message.photo:
                    await message.bot.send_photo(
                        chat_id=user_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption or ""
                    )
                elif message.document:
                    await message.bot.send_document(
                        chat_id=user_id,
                        document=message.document.file_id,
                        caption=message.caption or ""
                    )
                else:
                    await message.bot.send_message(
                        chat_id=user_id,
                        text=message.text
                    )
                success_count += 1
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
                failed_count += 1
        
        # Отправляем отчет о рассылке
        report_text = (
            f"📢 **Рассылка завершена**\n\n"
            f"✅ **Успешно отправлено:** {success_count}\n"
            f"❌ **Ошибок:** {failed_count}\n"
            f"📊 **Всего получателей:** {len(user_ids)}"
        )
        
        await message.answer(report_text, reply_markup=get_admin_menu())
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при массовой рассылке: {e}")
        await message.answer("Ошибка при выполнении рассылки", reply_markup=get_admin_menu())
        await state.clear()


@router.callback_query(F.data == "admin_stats")
@admin_check
async def admin_stats_handler(callback: CallbackQuery):
    """Обработчик статистики для админов"""
    await show_stats(callback)


@router.callback_query(F.data == "admin_broadcast")
@admin_check
async def admin_broadcast_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик рассылки для админов"""
    await start_broadcast(callback, state)
