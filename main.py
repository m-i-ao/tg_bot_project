import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from utils.db import init_db
from handlers.user import router as user_router
from handlers.admin import router as admin_router
from scheduler import start_scheduler
import config

# === Логирование ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# === Запуск Flask (веб-панель + Mini App API) ===
def run_flask():
    from web_app import app
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

# === Основная функция ===
async def main():
    # Инициализация бота
    bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключение роутеров
    dp.include_router(user_router)
    dp.include_router(admin_router)

    # Инициализация базы данных
    init_db()
    print("База данных инициализирована")

    # Запуск планировщика (бэкап, статистика, автопостинг)
    start_scheduler(bot)
    print("Планировщик запущен")

    # Запуск веб-панели в отдельном потоке
    import threading
    threading.Thread(target=run_flask, daemon=True).start()
    print("Веб-панель запущена: http://localhost:5000")

    # Удаление вебхука и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот запущен в режиме polling...")

    # Основной цикл
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен пользователем.")
    finally:
        await bot.session.close()
        print("Сессия закрыта.")

# === Запуск ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Критическая ошибка: {e}")