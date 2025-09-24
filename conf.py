import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# Ссылка на аккаунт менеджера
MANAGER_URL = os.getenv("MANAGER_URL", "")

# Подключение к Postgres
# формат: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://bot_user:bot_password@db:5432/bot_db")

# ID супергруппы для логирования
LOGGING_SUPERGROUP_ID = int(os.getenv("LOGGING_SUPERGROUP_ID", "-1001234567890"))

# Админские ID (через запятую)
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
