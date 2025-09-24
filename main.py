import asyncio
import sys
import subprocess
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from conf import BOT_TOKEN
from middlewares.logging import LoggingMiddleware
from handlers import start, about, tariffs, faq, admin, global_handler, referral, admin_resp, admin_places

# Настройка логирования
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("bot.log", rotation="1 day", retention="7 days", level="DEBUG")


async def main():
    """Главная функция бота"""
    logger.info("Запуск бота...")
    
    # Применяем миграции базы данных
    logger.info("Применение миграций базы данных...")
    try:
        result = subprocess.run(["alembic", "upgrade", "heads"], 
                              capture_output=True, text=True, check=True)
        logger.info("Миграции успешно применены")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка применения миграций: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return
    except Exception as e:
        logger.error(f"Неожиданная ошибка при применении миграций: {e}")
        return
    
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(about.router)
    dp.include_router(tariffs.router)
    dp.include_router(faq.router)
    dp.include_router(admin.router)
    dp.include_router(referral.router)
    dp.include_router(admin_resp.router)
    dp.include_router(admin_places.router)
    dp.include_router(global_handler.router)
    
    # Запуск бота
    try:
        logger.info("Бот запущен")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
