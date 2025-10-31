from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from menus import (
    get_main_menu, get_moderation_menu, get_stats_menu,
    get_backup_menu, get_roles_menu
)
from utils.db import get_user_role 
from aiogram.types import FSInputFile
from posting import post_from_folder, post_batch_from_multiple_sources
from backup import create_backup_channel, run_backup_cycle
from download import download_channel_history
from stats import send_stats_report, send_top_users
from roles import is_admin, init_admin, set_user_role
import config
import asyncio

router = Router()

# Инициализация админа
init_admin()

@router.callback_query(F.data == "main")
async def back_to_main(call: CallbackQuery):
    role = get_user_role(call.from_user.id)
    await call.message.edit_text("Главное меню:", reply_markup=get_main_menu(role))
    await call.answer()

@router.callback_query(F.data == "moderate")
async def show_moderation(call: CallbackQuery):
    if not is_admin(call.from_user.id) and get_user_role(call.from_user.id) != 'moderator':
        await call.answer("Нет доступа.")
        return
    await call.message.edit_text("Модерация:", reply_markup=get_moderation_menu())
    await call.answer()

@router.callback_query(F.data.startswith("view_"))
async def view_proposal(call: CallbackQuery):
    prop_id = int(call.data.split("_")[1])
    from db import get_conn
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT file_path, user_id FROM proposals WHERE id = ?', (prop_id,))
    row = c.fetchone()
    conn.close()
    if row:
        file_path, user_id = row
        from menus import get_proposal_keyboard
        await call.message.bot.send_photo(
            call.message.chat.id,
            FSInputFile(file_path),
            caption=f"Предложка от {user_id}",
            reply_markup=get_proposal_keyboard(prop_id)
        )
    await call.answer()

@router.callback_query(F.data == "stats")
async def show_stats_menu(call: CallbackQuery):
    await call.message.edit_text("Выберите период:", reply_markup=get_stats_menu())
    await call.answer()

@router.callback_query(F.data.startswith("stats_"))
async def stats_period(call: CallbackQuery):
    period = call.data.split("_")[1]
    await send_stats_report(call.bot, call.message.chat.id, period)
    await call.answer()

@router.callback_query(F.data == "top_users")
async def top_users(call: CallbackQuery):
    await send_top_users(call.bot, call.message.chat.id)
    await call.answer()

@router.callback_query(F.data == "backup")
async def show_backup_menu(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Только админ.")
        return
    await call.message.edit_text("Бэкап:", reply_markup=get_backup_menu())
    await call.answer()

@router.callback_query(F.data == "create_backup")
async def create_backup(call: CallbackQuery):
    chat_id, _ = await create_backup_channel(call.bot)
    if chat_id:
        await call.message.edit_text(f"Создан бэкап-канал: {chat_id}")
    else:
        await call.message.edit_text("Ошибка создания.")
    await call.answer()

@router.callback_query(F.data == "download_channel")
async def start_download(call: CallbackQuery):
    await call.message.edit_text("Скачивание начато...")
    downloaded = await download_channel_history(call.bot, config.SOURCE_CHANNEL_ID, limit=100)
    await call.message.edit_text(f"Скачано {downloaded} файлов в {config.DOWNLOADS_DIR}")
    await call.answer()

@router.callback_query(F.data == "roles")
async def show_roles_menu(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Только админ.")
        return
    await call.message.edit_text("Управление ролями:", reply_markup=get_roles_menu())
    await call.answer()

@router.message(Command("post_folder"))
async def cmd_post_folder(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Отправьте путь к папке (через /post_folder /path/to/folder)")
    # Реализация через состояние — упрощённо