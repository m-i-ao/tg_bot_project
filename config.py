import os
from dotenv import load_dotenv

load_dotenv()

# === ОСНОВНЫЕ НАСТРОЙКИ ===
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

# === ID КАНАЛОВ (замени на свои!) ===
SOURCE_CHANNEL_ID = -1001234567890   # откуда берём
TARGET_CHANNEL_ID = -1009876543210   # куда постим
BACKUP_CHANNEL_ID = None             # создадим динамически

# === АДМИН ===
ADMIN_ID = 123456789  # твой ID (узнай через @userinfobot)

# === ПАПКИ ===
PENDING_IMAGES_DIR = 'pending_images'
DOWNLOADS_DIR = 'downloads'
BACKUPS_DIR = 'backups'
os.makedirs(PENDING_IMAGES_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

# === БАЗА ДАННЫХ ===
DB_FILE = 'bot.db'

# === ФИЛЬТРЫ ПО УМОЛЧАНИЮ ===
DEFAULT_FILTERS = {
    'type': ['.jpg', '.png'],
    'max_size_mb': 10,
    'min_days_old': 0,
    'nsfw': False
}

# === РАСПИСАНИЕ ===
POSTING_CRON = '0 */6 * * *'  # каждые 6 часов
STATS_CRON = '0 0 * * *'     # каждый день в 00:00