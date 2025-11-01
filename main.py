# main.py
import asyncio
import threading
from utils.db import init_db
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.admin import router as admin_router
from handlers.user import router as user_router
from roles import init_admin
from web_app import run_flask
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.admin import router as admin_router
from handlers.user import router as user_router
from utils.db import init_db  # ← ДОБАВЬ

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(user_router)

# ← ДОБАВЬ ЭТУ СТРОКУ:
init_db()  # Создаёт таблицы: users, proposals и т.д.

if __name__ == "__main__":
    print("Бот запущен...")
    dp.run_polling(bot)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключение роутеров
dp.include_router(admin_router)
dp.include_router(user_router)

def main():
    # 1. Сначала инициализируем БД
    init_db()
    print("База данных инициализирована")

    # 2. Потом — админа
    init_admin()

    # 3. Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Веб-панель запущена: http://localhost:5000")

    # 4. Запускаем бота
    print("Бот запущен...")
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()