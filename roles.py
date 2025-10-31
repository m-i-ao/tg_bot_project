from utils.db import get_user_role, set_user_role
import config

def is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID or get_user_role(user_id) == 'admin'

def is_moderator(user_id: int) -> bool:
    role = get_user_role(user_id)
    return role in ['moderator', 'admin']

def require_role(role: str):
    """Декоратор для хендлеров"""
    def decorator(handler):
        async def wrapper(message, *args, **kwargs):
            user_id = message.from_user.id
            current_role = get_user_role(user_id)
            roles_hierarchy = {'user': 0, 'moderator': 1, 'admin': 2}
            if roles_hierarchy.get(current_role, 0) >= roles_hierarchy.get(role, 0):
                return await handler(message, *args, **kwargs)
            else:
                await message.answer("Доступ запрещён.")
        return wrapper
    return decorator

# Инициализация админа
def init_admin():
    set_user_role(config.ADMIN_ID, 'admin', 'Admin', 'Bot Admin')