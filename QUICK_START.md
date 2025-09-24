# 🚀 Быстрый запуск бота

## 1. Настройка переменных окружения

```bash
cp env.example .env
```

Отредактируйте `.env` файл:
```env
BOT_TOKEN=your_bot_token_here
MANAGER_URL=https://t.me/your_manager
LOGGING_SUPERGROUP_ID=-1001234567890
ADMIN_IDS=123456789,987654321
```

## 2. Запуск с Docker Compose

```bash
docker-compose up -d
```

## 3. Применение миграций

```bash
docker-compose exec bot alembic upgrade head
```

## 4. Проверка логов

```bash
docker-compose logs -f bot
```

## 5. Остановка

```bash
docker-compose down
```

## 🔧 Устранение проблем

### Ошибка с базой данных
```bash
docker-compose restart db
docker-compose restart bot
```

### Пересборка образа
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Просмотр статуса
```bash
docker-compose ps
```
