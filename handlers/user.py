from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from db import add_proposal, get_user_role, set_user_role
from utils import download_file
from posting import post_single_photo
import config
import os
from utils.db import update_proposal_status

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    role = get_user_role(user_id)
    if role == 'user' and user_id != config.ADMIN_ID:
        set_user_role(user_id, 'user', message.from_user.username, message.from_user.first_name)
    from menus import get_main_menu
    await message.answer(
        "Привет! Это бот для управления контентом.\n"
        "Используй кнопки ниже:",
        reply_markup=get_main_menu(role)
    )

@router.callback_query(F.data == "propose")
async def propose_photo(call: CallbackQuery):
    await call.message.answer("Отправьте фото для предложки.")
    await call.answer()

@router.message(F.photo)
async def receive_photo(message: Message):
    user_id = message.from_user.id
    role = get_user_role(user_id)
    if role != 'user' and user_id != config.ADMIN_ID:
        await message.answer("Только пользователи могут предлагать.")
        return

    file_id = message.photo[-1].file_id
    file_path = os.path.join(config.PENDING_IMAGES_DIR, f"prop_{user_id}_{file_id}.jpg")
    downloaded = await download_file(message.bot, file_id, file_path)
    if not downloaded:
        await message.answer("Ошибка загрузки.")
        return

    proposal_id = add_proposal(user_id, file_id, file_path, message.message_id)
    await message.answer(f"Фото получено! ID: {proposal_id}\nОжидает модерации.")

@router.callback_query(F.data.startswith("approve_"))
async def approve_proposal(call: CallbackQuery):
    if not get_user_role(call.from_user.id) in ['moderator', 'admin']:
        await call.answer("Нет доступа.")
        return
    prop_id = int(call.data.split("_")[1])
    update_proposal_status(prop_id, 'approved')
    # Найдём путь
    from db import get_conn
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT file_path FROM proposals WHERE id = ?', (prop_id,))
    row = c.fetchone()
    conn.close()
    if row:
        file_path = row[0]
        await post_single_photo(call.bot, file_path, config.TARGET_CHANNEL_ID)
        os.remove(file_path)
    await call.message.edit_text(f"Предложка {prop_id} одобрена.")
    await call.answer()

@router.callback_query(F.data.startswith("reject_"))
async def reject_proposal(call: CallbackQuery):
    if not get_user_role(call.from_user.id) in ['moderator', 'admin']:
        await call.answer("Нет доступа.")
        return
    prop_id = int(call.data.split("_")[1])
    update_proposal_status(prop_id, 'rejected')
    await call.message.edit_text(f"Предложка {prop_id} отклонена.")
    await call.answer()

@router.callback_query(F.data == "help")
async def help_cmd(call: CallbackQuery):
    await call.message.answer(
        "Помощь:\n"
        "/start — главное меню\n"
        "Предложка — отправь фото\n"
        "Модерация — только для модераторов\n"
        "Бэкап — дублирование контента"
    )
    await call.answer()