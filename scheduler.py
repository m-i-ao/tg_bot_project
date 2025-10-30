from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backup import run_backup_cycle
from stats import generate_stats_graph
from posting import post_from_folder
import config
import asyncio
import os

scheduler = AsyncIOScheduler()

async def auto_backup_task(bot):
    await run_backup_cycle(bot)

async def auto_stats_task(bot):
    graph_path = generate_stats_graph()
    if graph_path and os.path.exists(graph_path):
        await bot.send_photo(config.ADMIN_ID, open(graph_path, 'rb'), caption="Авто-статистика")
        os.remove(graph_path)

async def auto_post_from_folder(bot):
    if os.path.exists('auto_post_folder'):
        await post_from_folder(bot, 'auto_post_folder', batch_size=5, delay=3)

def start_scheduler(bot):
    # Авто-бэкап каждые 6 часов
    scheduler.add_job(
        auto_backup_task,
        'cron',
        args=(bot,),
        hour='*/6',
        id='backup_job'
    )

    # Авто-статистика каждый день в 00:00
    scheduler.add_job(
        auto_stats_task,
        'cron',
        args=(bot,),
        hour=0,
        minute=0,
        id='stats_job'
    )

    # Авто-постинг из папки auto_post_folder каждые 30 мин
    scheduler.add_job(
        auto_post_from_folder,
        'cron',
        args=(bot,),
        minute='*/30',
        id='autopost_job'
    )

    scheduler.start()
    print("Планировщик запущен: бэкап, статистика, автопостинг")