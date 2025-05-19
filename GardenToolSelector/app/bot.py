import asyncio
import logging #Потом выключить

from aiogram import Bot, Dispatcher

from app.config import TOKEN
from app.handlers import main_router
from app.database import init_db

# Объект бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Запуск процесса поллинга новых апдейтов
async def main():
    # Инициализация БД
    await init_db()
    dp.include_router(main_router)
    await dp.start_polling(bot)
    print('Бот запущен')


if __name__ == "__main__":
    # Потом выключить
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')