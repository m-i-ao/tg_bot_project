import os
import asyncio
import utils
from aiogram import Bot
from utils.filters import file_passes_filters 
from tqdm import tqdm
from utils import download_file
import config

async def download_channel_history(bot: Bot, chat_id: int, limit: int = 1000, output_dir: str = None):
    output_dir = output_dir or config.DOWNLOADS_DIR
    os.makedirs(output_dir, exist_ok=True)
    downloaded = 0
    pbar = tqdm(total=limit, desc="Скачивание")
    try:
        async for message in bot.iter_history(chat_id, limit=limit):
            if message.photo:
                file_id = message.photo[-1].file_id
                file_path = os.path.join(output_dir, f"{file_id}.jpg")
                if await download_file(bot, file_id, file_path):
                    downloaded += 1
                    pbar.update(1)
            elif message.document and message.document.mime_type.startswith('image/'):
                file_path = os.path.join(output_dir, message.document.file_name)
                if await download_file(bot, message.document.file_id, file_path):
                    downloaded += 1
                    pbar.update(1)
            await asyncio.sleep(0.1)
        pbar.close()
        return downloaded
    except Exception as e:
        pbar.close()
        print(f"Download error: {e}")
        return 0

async def download_batch_with_filters(bot: Bot, chat_id: int, filters: dict, count: int = 100):
    collected = []
    async for msg in bot.iter_history(chat_id, limit=count * 2):
        if msg.photo:
            file_id = msg.photo[-1].file_id
            temp_path = os.path.join(config.PENDING_IMAGES_DIR, f"temp_{file_id}.jpg")
            if await download_file(bot, file_id, temp_path):
                if file_passes_filters(temp_path, filters):
                    collected.append(temp_path)
                else:
                    os.remove(temp_path)
        if len(collected) >= count:
            break
    return collected