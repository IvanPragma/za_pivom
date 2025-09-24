from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from conf import ADMIN_IDS
from utils.config import load_config, set_fake_occupied, get_remaining_places, get_max_places, set_max_places
from database.base import get_session
from database.models import User, Payment
from sqlalchemy import select, func
from loguru import logger

router = Router()


@router.message(Command("places"))
async def show_places_info(message: Message):
    """Показывает информацию о местах (только для админов)"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
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
        
        # Получаем конфиг
        config = load_config()
        fake_occupied = config["fake_occupied"]
        max_places = config["max_places"]
        
        # Рассчитываем оставшиеся места
        remaining_places = max_places - users_with_subscription - fake_occupied
        
        places_info = (
            f"📊 <b>Информация о местах</b>\n\n"
            f"👥 Пользователей с подпиской: {users_with_subscription}\n"
            f"🎭 Накрученных мест: {fake_occupied}\n"
            f"📈 Максимум мест: {max_places}\n"
            f"🔥 Осталось мест: {remaining_places}\n\n"
            f"<b>Команды:</b>\n"
            f"/set_fake &lt;число&gt; - установить накрутку\n"
            f"/set_max &lt;число&gt; - установить максимум мест\n"
            f"/reset_fake - сбросить накрутку"
        )
        
        await message.answer(places_info, parse_mode="HTML")
        
    finally:
        await session.close()


@router.message(Command("set_fake"))
async def set_fake_places(message: Message):
    """Устанавливает количество накрученных мест (только для админов)"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    try:
        # Получаем число из команды
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Использование: /set_fake <число>")
            return
        
        fake_count = int(parts[1])
        if fake_count < 0:
            await message.answer("❌ Количество не может быть отрицательным")
            return
        
        if fake_count > 20:
            await message.answer("❌ Количество не может быть больше 20")
            return
        
        # Устанавливаем накрутку
        set_fake_occupied(fake_count)
        
        # Получаем актуальную информацию
        session = await get_session()
        try:
            users_with_subscription = await session.scalar(
                select(func.count(func.distinct(User.id)))
                .select_from(User)
                .join(Payment, User.id == Payment.user_id)
                .where(Payment.status == "paid")
            ) or 0
            
            remaining_places = get_remaining_places() - users_with_subscription
            
            await message.answer(
                f"✅ Накрутка установлена: {fake_count} мест\n"
                f"🔥 Осталось мест: {remaining_places}/20"
            )
            
            logger.info(f"Админ {message.from_user.id} установил накрутку: {fake_count} мест")
            
        finally:
            await session.close()
            
    except ValueError:
        await message.answer("❌ Неверный формат числа")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        logger.error(f"Ошибка установки накрутки: {e}")


@router.message(Command("reset_fake"))
async def reset_fake_places(message: Message):
    """Сбрасывает накрутку (только для админов)"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    try:
        # Сбрасываем накрутку
        set_fake_occupied(0)
        
        # Получаем актуальную информацию
        session = await get_session()
        try:
            users_with_subscription = await session.scalar(
                select(func.count(func.distinct(User.id)))
                .select_from(User)
                .join(Payment, User.id == Payment.user_id)
                .where(Payment.status == "paid")
            ) or 0
            
            remaining_places = get_remaining_places() - users_with_subscription
            
            await message.answer(
                f"✅ Накрутка сброшена\n"
                f"🔥 Осталось мест: {remaining_places}/20"
            )
            
            logger.info(f"Админ {message.from_user.id} сбросил накрутку")
            
        finally:
            await session.close()
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        logger.error(f"Ошибка сброса накрутки: {e}")


@router.message(Command("set_max"))
async def set_max_places_command(message: Message):
    """Устанавливает максимальное количество мест (только для админов)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❌ Использование: /set_max &lt;число&gt;")
            return
        
        new_max = int(args[1])
        if new_max < 1:
            await message.answer("❌ Количество мест должно быть больше 0")
            return
        
        # Проверяем, что новое значение не меньше текущих подписок
        session = await get_session()
        try:
            users_with_subscription = await session.scalar(
                select(func.count(func.distinct(User.id)))
                .select_from(User)
                .join(Payment, User.id == Payment.user_id)
                .where(Payment.status == "paid")
            ) or 0
            
            if new_max < users_with_subscription:
                await message.answer(
                    f"❌ Нельзя установить максимум меньше текущих подписок ({users_with_subscription})"
                )
                return
            
            set_max_places(new_max)
            
            # Пересчитываем оставшиеся места
            config = load_config()
            fake_occupied = config["fake_occupied"]
            remaining_places = new_max - users_with_subscription - fake_occupied
            
            await message.answer(
                f"✅ Максимум мест установлен: {new_max}\n"
                f"🔥 Осталось мест: {remaining_places}/{new_max}"
            )
            
            logger.info(f"Админ {message.from_user.id} установил максимум мест: {new_max}")
            
        finally:
            await session.close()
            
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
