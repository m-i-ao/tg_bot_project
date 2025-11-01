from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.admin import router as admin_router
from handlers.user import router as user_router
from utils.db import init_db
from web_app import run_flask
import threading

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(user_router)

init_db()  # Создаёт таблицы users, proposals для aiogram

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

if __name__ == "__main__":
    print("Бот запущен...")
    print("Веб-панель: http://127.0.0.1:5000")
    dp.run_polling(bot)