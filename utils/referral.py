import string
import random
from database.base import get_session
from database.models import User
from sqlalchemy import select


def generate_referral_code(length: int = 6) -> str:
    """Генерирует случайный реферальный код из букв и цифр"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def get_unique_referral_code() -> str:
    """Генерирует уникальный реферальный код, которого нет в базе данных"""
    while True:
        code = generate_referral_code()
        session = await get_session()
        try:
            result = await session.execute(select(User).where(User.referral_code == code))
            existing_user = result.scalar_one_or_none()
            if not existing_user:
                return code
        finally:
            await session.close()


async def get_user_by_referral_code(referral_code: str) -> User | None:
    """Находит пользователя по реферальному коду"""
    session = await get_session()
    try:
        result = await session.execute(select(User).where(User.referral_code == referral_code))
        return result.scalar_one_or_none()
    finally:
        await session.close()
