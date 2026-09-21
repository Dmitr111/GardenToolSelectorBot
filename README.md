# GardenToolSelectorBot

Telegram-бот для подбора садового инвентаря: каталог инструментов с фильтрами и поиском,
сравнение, избранное, отзывы, рекомендации с учётом уровня подготовки пользователя и
админ-панель для управления каталогом.

> **Учебный проект.** Это моя курсовая работа. Бот не развёрнут и больше не работает
> (удалён через BotFather); репозиторий сохранён как пример кода.

## Стек

- Python 3.11+
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot API (FSM, роутеры)
- SQLAlchemy 2 (async) + asyncpg — работа с PostgreSQL
- python-dotenv — конфигурация из `.env`

## Структура

```
app/
├── bot.py            # точка входа
├── config.py         # чтение переменных окружения
├── database/
│   ├── db.py         # движок, инициализация БД и начальные данные
│   ├── models/       # модели SQLAlchemy
│   └── repositories/ # доступ к данным
├── handlers/         # обработчики команд и колбэков (в т.ч. admin/)
└── keyboards/        # inline-клавиатуры
```

## Запуск

1. Создайте бота у [@BotFather](https://t.me/BotFather) и базу PostgreSQL.
2. Установите зависимости:
   ```
   python -m venv venv
   venv\Scripts\activate      # Linux/macOS: source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Создайте `.env` в корне репозитория на основе примера:
   ```
   cp .env.example .env
   ```
   | Переменная     | Обязательна | Описание |
   |----------------|-------------|----------|
   | `BOT_TOKEN`    | да | токен от BotFather |
   | `DATABASE_URL` | да | `postgresql+asyncpg://user:password@host:port/db` |
   | `ADMIN_IDS`    | нет | Telegram ID администраторов через запятую |

   Если обязательная переменная не задана, бот завершится с сообщением об ошибке.
4. Запустите бота (таблицы и начальные данные создаются автоматически):
   ```
   python -m app.bot
   ```
