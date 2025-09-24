from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import get_main_menu

router = Router()


@router.callback_query(F.data == "about")
async def about_service(callback: CallbackQuery):
    """Обработчик раздела 'О сервисе'"""
    about_text = (
        "🎓 <b>О сервисе</b>\n\n"
        "Мы помогаем студентам закрыть физру без лишней беготни и траты времени.\n\n"
        "⚙️ <b>Как это работает?</b>\n"
        "- Наши исполнители ходят на занятия вместо вас.\n"
        "- Баллы начисляются стабильно, вы уверенно идёте к заветным 100.\n\n"
        "✅ <b>Почему это удобно?</b>\n"
        "- Экономия времени и нервов.\n"
        "- Надёжные исполнители, проверенные опытом.\n"
        "- Гарантия: возвращаем деньги за неиспользованные баллы.\n\n"
        "💡 <b>Для кого?</b>\n"
        "- Для тех, у кого плотный график.\n"
        "- Для студентов, которые ценят своё время.\n\n"
        "Просто, удобно и без лишних вопросов 👍"
    )
    
    await callback.message.edit_text(
        about_text,
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()
