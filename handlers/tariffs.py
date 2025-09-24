from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import get_tariffs_menu, get_main_menu
from conf import MANAGER_URL
from middlewares.helpers import forward_bot_message_to_user_topic

router = Router()


@router.callback_query(F.data == "tariffs")
async def show_tariffs(callback: CallbackQuery):
    """Показывает меню тарифов"""
    tariffs_text = (
        "У нас есть 2 варианта подключения сервиса:\n\n"
        "🔥 Моментальный тариф\n"
        "Стоимость: 4400 ₽\n"
        "Оплата сразу за семестр.\n\n"
        "💳 Тариф в рассрочку:\n"
        "- 6 месяцев: 850 ₽/мес (итого 5280 ₽)\n"
        "- 3 месяца: 1700 ₽/мес (итого 5100 ₽)\n"
        "- 2 месяца: 2450 ₽/мес (итого 4900 ₽)\n\n"
        "После выбора тарифа вы будете перенаправлены к нашему менеджеру."
    )
    
    sent = await callback.message.edit_text(
        tariffs_text,
        reply_markup=get_tariffs_menu()
    )
    await forward_bot_message_to_user_topic(callback.bot, sent, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("tariff_"))
async def select_tariff(callback: CallbackQuery):
    """Обработчик выбора тарифа"""
    tariff_data = {
        "tariff_instant": "🔥 Моментальный тариф - 4400₽",
        "tariff_6m": "💳 6 месяцев - 850₽/мес (итого 5280₽)",
        "tariff_3m": "💳 3 месяца - 1700₽/мес (итого 5100₽)",
        "tariff_2m": "💳 2 месяца - 2450₽/мес (итого 4900₽)"
    }
    
    selected_tariff = tariff_data.get(callback.data, "Выбранный тариф")
    
    response_text = (
        f"Вы выбрали: {selected_tariff}\n\n"
        "Для оформления заказа свяжитесь с нашим менеджером:\n"
        f"{MANAGER_URL}"
    )
    
    sent = await callback.message.edit_text(
        response_text,
        reply_markup=get_main_menu()
    )
    await forward_bot_message_to_user_topic(callback.bot, sent, callback.from_user.id)
    await callback.answer()
