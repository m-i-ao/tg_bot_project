import os
import aiohttp
import cv2
import numpy as np
from PIL import Image
from utils.ai_filter import is_image_nsfw
from datetime import datetime, timedelta
import config

async def download_file(bot, file_id, dest_path):
    try:
        file = await bot.get_file(file_id)
        url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(dest_path, 'wb') as f:
                        f.write(await resp.read())
                    return dest_path
        return None
    except Exception as e:
        print(f"Download error: {e}")
        return None

def is_image_nsfw(image_path, threshold=0.3):
    """Простая проверка на NSFW по доле кожи (цвет)"""
    try:
        img = cv2.imread(image_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        skin_ratio = cv2.countNonZero(mask) / (img.shape[0] * img.shape[1])
        return skin_ratio > threshold
    except:
        return False

def file_passes_filters(file_path, filters):
    if not os.path.exists(file_path):
        return False

    # Тип
    ext = os.path.splitext(file_path)[1].lower()
    if 'type' in filters and ext not in filters['type']:
        return False

    # Размер
    if 'max_size_mb' in filters:
        if os.path.getsize(file_path) > filters['max_size_mb'] * 1024 * 1024:
            return False

    # Давность
    if 'min_days_old' in filters:
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if datetime.now() - file_time < timedelta(days=filters['min_days_old']):
            return False

    # NSFW
    if filters.get('nsfw') == False:
        if is_image_nsfw(file_path):
            return False

    return True

def get_file_age_days(file_path):
    return (datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))).days

# Добавь в конец utils.py:


async def is_image_nsfw(image_path):  # Теперь async!
    return await is_image_nsfw(image_path)