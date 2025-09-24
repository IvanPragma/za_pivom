from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from conf import MANAGER_URL

def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    keyboard = [
        [InlineKeyboardButton(text="📋 О сервисе", callback_data="about")],
        [InlineKeyboardButton(text="💰 Тарифы", callback_data="tariffs")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton(text="🎁 Реферальная система", callback_data="referral")],
        [InlineKeyboardButton(text="📞 Связаться с менеджером", url=MANAGER_URL)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_tariffs_menu() -> InlineKeyboardMarkup:
    """Меню тарифов"""
    keyboard = [
        [InlineKeyboardButton(text="🔥 Моментальный тариф - 4400₽", callback_data="tariff_instant")],
        [InlineKeyboardButton(text="💳 6 месяцев - 850₽/мес", callback_data="tariff_6m")],
        [InlineKeyboardButton(text="💳 3 месяца - 1700₽/мес", callback_data="tariff_3m")],
        [InlineKeyboardButton(text="💳 2 месяца - 2450₽/мес", callback_data="tariff_2m")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_faq_menu() -> InlineKeyboardMarkup:
    """Меню FAQ"""
    keyboard = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_menu() -> InlineKeyboardMarkup:
    """Админское меню"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Массовая рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
