import os
import asyncio
from aiogram import Bot
from aiogram.types import InputFile
from utils.utils import download_file, file_passes_filters
from utils.db import log_post
import config

async def post_single_photo(bot: Bot, photo_path: str, chat_id: int = None):
    if not file_passes_filters(photo_path, config.DEFAULT_FILTERS):
        return None
    chat_id = chat_id or config.TARGET_CHANNEL_ID
    try:
        with open(photo_path, 'rb') as f:
            msg = await bot.send_photo(chat_id, InputFile(f))
        return msg.message_id
    except Exception as e:
        print(f"Post error: {e}")
        return None

async def post_from_channel(bot: Bot, source_msg_id: int, target_chat_id: int = None, use_copy=False):
    try:
        msg = await bot.get_chat_message(config.SOURCE_CHANNEL_ID, source_msg_id)
        if not msg.photo:
            return None
        file_id = msg.photo[-1].file_id
        temp_path = os.path.join(config.PENDING_IMAGES_DIR, f"{file_id}.jpg")
        await download_file(bot, file_id, temp_path)
        if not file_passes_filters(temp_path, config.DEFAULT_FILTERS):
            os.remove(temp_path)
            return None
        target_id = target_chat_id or config.TARGET_CHANNEL_ID
        if use_copy:
            sent = await bot.copy_message(
                chat_id=target_id,
                from_chat_id=config.SOURCE_CHANNEL_ID,
                message_id=source_msg_id
            )
            target_msg_id = sent.message_id
        else:
            target_msg_id = await post_single_photo(bot, temp_path, target_id)
            os.remove(temp_path)
        log_post(config.SOURCE_CHANNEL_ID, source_msg_id, target_msg_id, 'photo')
        return target_msg_id
    except Exception as e:
        print(f"Channel post error: {e}")
        return None

async def post_from_folder(bot: Bot, folder_path: str, batch_size: int = 10, delay: int = 2, filters: dict = None):
    filters = filters or config.DEFAULT_FILTERS
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
    posted = 0
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        for file in batch:
            file_path = os.path.join(folder_path, file)
            if file_passes_filters(file_path, filters):
                await post_single_photo(bot, file_path)
                posted += 1
            await asyncio.sleep(delay)
    return posted

async def post_batch_from_multiple_sources(bot: Bot, sources: list, count: int = 10, filters: dict = None):
    """sources = [{'type': 'folder', 'path': '/path'}, {'type': 'channel', 'id': -100...}]"""
    collected = []
    for src in sources:
        if src['type'] == 'folder':
            files = [os.path.join(src['path'], f) for f in os.listdir(src['path']) if f.lower().endswith(('.jpg', '.png'))]
            collected.extend(files)
        elif src['type'] == 'channel':
            # Простой сбор последних 50
            try:
                async for msg in bot.iter_history(src['id'], limit=50):
                    if msg.photo:
                        collected.append(('channel', src['id'], msg.message_id))
            except:
                pass
    collected = [f for f in collected if isinstance(f, str) and file_passes_filters(f, filters or {})]
    collected = collected[:count]
    posted = 0
    for item in collected:
        if isinstance(item, str):
            await post_single_photo(bot, item)
        else:
            await post_from_channel(bot, item[2], use_copy=True)
        posted += 1
        await asyncio.sleep(1)
    return posted