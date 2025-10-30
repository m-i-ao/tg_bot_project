from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import get_pending_proposals, update_proposal_status
import config

def get_main_menu(user_role: str):
    kb = []
    if user_role == 'user':
        kb.append([InlineKeyboardButton("Предложить фото", callback_data="propose")])
    if user_role in ['moderator', 'admin']:
        kb.append([InlineKeyboardButton("Модерация", callback_data="moderate")])
        kb.append([InlineKeyboardButton("Статистика", callback_data="stats")])
        kb.append([InlineKeyboardButton("Бэкап", callback_data="backup")])
    if user_role == 'admin':
        kb.append([InlineKeyboardButton("Управление ролями", callback_data="roles")])
        kb.append([InlineKeyboardButton("Настройки", callback_data="settings")])
    kb.append([InlineKeyboardButton("Помощь", callback_data="help")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_proposal_keyboard(proposal_id: int):
    kb = [
        [InlineKeyboardButton("Одобрить", callback_data=f"approve_{proposal_id}")],
        [InlineKeyboardButton("Отклонить", callback_data=f"reject_{proposal_id}")],
        [InlineKeyboardButton("Назад", callback_data="moderate")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_moderation_menu():
    proposals = get_pending_proposals()
    kb = []
    for prop_id, file_path, user_id, msg_id in proposals[:10]:  # лимит 10
        kb.append([InlineKeyboardButton(
            f"Предложка от {user_id} [{prop_id}]",
            callback_data=f"view_{prop_id}"
        )])
    if not kb:
        kb.append([InlineKeyboardButton("Нет предложек", callback_data="none")])
    kb.append([InlineKeyboardButton("Обновить", callback_data="moderate")])
    kb.append([InlineKeyboardButton("Назад", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_stats_menu():
    kb = [
        [InlineKeyboardButton("За день", callback_data="stats_day")],
        [InlineKeyboardButton("За неделю", callback_data="stats_week")],
        [InlineKeyboardButton("За месяц", callback_data="stats_month")],
        [InlineKeyboardButton("Топ пользователей", callback_data="top_users")],
        [InlineKeyboardButton("Назад", callback_data="main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_backup_menu():
    kb = [
        [InlineKeyboardButton("Создать бэкап-канал", callback_data="create_backup")],
        [InlineKeyboardButton("Переслать с ID", callback_data="forward_from")],
        [InlineKeyboardButton("Скачать канал", callback_data="download_channel")],
        [InlineKeyboardButton("Назад", callback_data="main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_roles_menu():
    kb = [
        [InlineKeyboardButton("Добавить модератора", callback_data="add_moderator")],
        [InlineKeyboardButton("Список модераторов", callback_data="list_mods")],
        [InlineKeyboardButton("Назад", callback_data="main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)