# roles.py
from utils.db import get_user_role, set_user_role
from config import ADMIN_ID

def is_admin(user_id: int) -> bool:
    return get_user_role(user_id) == 'admin'

def is_moderator(user_id: int) -> bool:
    return get_user_role(user_id) in ('moderator', 'admin')

def require_role(role: str):
    def decorator(handler):
        async def wrapper(message, *args, **kwargs):
            user_role = get_user_role(message.from_user.id)
            if role == 'admin' and user_role != 'admin':
                await message.answer("У вас нет прав администратора.")
                return
            if role == 'moderator' and user_role not in ('moderator', 'admin'):
                await message.answer("У вас нет прав модератора.")
                return
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator

def init_admin():
    if not ADMIN_ID:
        print("ВНИМАНИЕ: ADMIN_ID не указан в config.py!")
        return
    try:
        set_user_role(ADMIN_ID, 'admin', 'Admin', 'Bot Admin')
        print(f"Админ инициализирован: {ADMIN_ID}")
    except Exception as e:
        print(f"Ошибка при инициализации админа: {e}")