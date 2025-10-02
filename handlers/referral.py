from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func
from keyboards.inline import get_main_menu
from database.base import get_session
from database.models import User, Payment

router = Router()


@router.callback_query(F.data == "referral")
async def show_referral_info(callback: CallbackQuery):
    """Показать информацию о реферальной системе"""
    tg_user_id = callback.from_user.id
    
    # Получаем пользователя из базы данных
    session = await get_session()
    try:
        result = await session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return
        
        # Получаем статистику рефералов
        # Количество приглашенных
        total_referrals = await session.scalar(
            select(func.count(User.id)).where(User.referrer_id == user.id)
        )
        
        # Количество с подпиской (у кого есть оплаченные платежи)
        referrals_with_subscription = await session.scalar(
            select(func.count(func.distinct(User.id)))
            .select_from(User)
            .join(Payment, User.id == Payment.user_id)
            .where(User.referrer_id == user.id, Payment.status == "paid")
        )
        
        # Сумма всех подписок рефералов (уникальные подписки, не дублируем рассрочки)
        from database.models import PaymentPlan
        # Сначала получаем уникальные комбинации user_id + plan_id
        unique_subscriptions = await session.execute(
            select(Payment.user_id, Payment.plan_id)
            .select_from(User)
            .join(Payment, User.id == Payment.user_id)
            .where(User.referrer_id == user.id)
            .distinct()
        )
        
        # Затем суммируем цены этих уникальных подписок
        total_referral_subscriptions = 0
        for user_id, plan_id in unique_subscriptions:
            plan_price = await session.scalar(
                select(PaymentPlan.price_total)
                .where(PaymentPlan.id == plan_id)
            )
            if plan_price:
                total_referral_subscriptions += plan_price
        
        # Заработано (пока всегда 0, функционал реализуем позже)
        earned_rub = 0
        # 20% от общей суммы подписок рефералов
        total_rub = int(total_referral_subscriptions * 0.2)
        
    finally:
        await session.close()
    
    referral_text = (
        "🎁 <b>Реферальная система</b>\n\n"
        "Приглашайте друзей и получайте <b>20% с каждой подписки</b> ваших рефералов!\n\n"
        "📊 <b>Ваша статистика:</b>\n"
        f"👥 Приглашено: {total_referrals}\n"
        f"💳 С подпиской: {referrals_with_subscription}\n"
        f"💰 Заработано: {earned_rub}₽ / {total_rub}₽\n\n"
        "📋 <b>Как это работает:</b>\n"
        "• Поделитесь своей реферальной ссылкой\n"
        "• Друг переходит по ссылке и регистрируется\n"
        "• При покупке подписки вы получаете 20% от суммы (вывести их можно после набора 20% баллов другом)\n\n"
        "🔗 <b>Ваша реферальная ссылка:</b>\n"
        f"<code>t.me/za_pivom_bot?start=ref{user.referral_code}</code>\n\n"
        "💡 Просто скопируйте ссылку и отправьте друзьям!"
    )
    
    keyboard = [
        [{"text": "🔙 Назад", "callback_data": "back_to_main"}]
    ]
    
    await callback.message.edit_text(
        referral_text, 
        reply_markup={"inline_keyboard": keyboard},
        parse_mode="HTML"
    )
    await callback.answer()
