import asyncio
from aiogram import Bot
from db import create_backup_record, get_active_backups, update_backup_last_id
import config

async def create_backup_channel(bot: Bot, title: str = "Backup Channel"):
    try:
        chat = await bot.create_chat(title=title, description="Автоматический бэкап")
        config.BACKUP_CHANNEL_ID = chat.id
        backup_id = create_backup_record(config.SOURCE_CHANNEL_ID, chat.id)
        return chat.id, backup_id
    except Exception as e:
        print(f"Create backup error: {e}")
        return None, None

async def forward_from_message_id(bot: Bot, from_chat_id: int, from_msg_id: int, to_chat_id: int, count: int = 100):
    posted = 0
    try:
        for i in range(count):
            msg_id = from_msg_id + i
            try:
                await bot.forward_message(
                    chat_id=to_chat_id,
                    from_chat_id=from_chat_id,
                    message_id=msg_id
                )
                posted += 1
            except:
                break
        return posted
    except Exception as e:
        print(f"Forward error: {e}")
        return 0

async def copy_interval_without_author(bot: Bot, from_chat_id: int, from_msg_id_start: int, from_msg_id_end: int, to_chat_id: int):
    posted = 0
    for msg_id in range(from_msg_id_start, from_msg_id_end + 1):
        try:
            await bot.copy_message(
                chat_id=to_chat_id,
                from_chat_id=from_chat_id,
                message_id=msg_id
            )
            posted += 1
            await asyncio.sleep(0.5)
        except:
            continue
    return posted

async def run_backup_cycle(bot: Bot):
    backups = get_active_backups()
    for src_id, backup_id, last_id in backups:
        try:
            async for msg in bot.iter_history(src_id, limit=50, offset_id=last_id):
                if msg.message_id <= last_id:
                    continue
                await bot.copy_message(backup_id, src_id, msg.message_id)
                last_id = msg.message_id
            update_backup_last_id(backups[0][0] if backups else 0, last_id)  # упрощённо
        except Exception as e:
            print(f"Backup cycle error: {e}")