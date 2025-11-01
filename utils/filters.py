import os
from utils.ai_filter import is_image_nsfw
from utils.utils import get_file_age_days
from datetime import datetime, timedelta
import config
from typing import List

def file_passes_filters(filepath: str, allowed_extensions: List[str] = None) -> bool:
    """
    Проверяет, проходит ли файл по фильтрам.
    Пока — просто проверка расширения.
    """
    if allowed_extensions is None:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.mp4', '.pdf', '.docx']

    ext = os.path.splitext(filepath)[1].lower()
    return ext in allowed_extensions

def apply_custom_filters(file_path: str, custom_filters: dict) -> bool:
    """
    Применяет пользовательские фильтры к файлу.
    custom_filters = {
        'type': ['.jpg', '.png'],
        'max_size_mb': 10,
        'min_days_old': 0,
        'nsfw': False,
        'max_count': 100
    }
    """
    if not os.path.exists(file_path):
        return False

    # === Тип файла ===
    if 'type' in custom_filters:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in [t.lower() for t in custom_filters['type']]:
            return False

    # === Размер ===
    if 'max_size_mb' in custom_filters:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > custom_filters['max_size_mb']:
            return False

    # === Давность ===
    if 'min_days_old' in custom_filters:
        age_days = get_file_age_days(file_path)
        if age_days < custom_filters['min_days_old']:
            return False

    # === NSFW ===
    if custom_filters.get('nsfw') is False:
        if is_image_nsfw(file_path):
            return False

    # === Дополнительно: можно добавить по количеству, выборке и т.д. ===
    return True

def get_filter_preset(preset_name: str) -> dict:
    """Предустановки фильтров"""
    presets = {
        'strict': {
            'type': ['.jpg', '.png'],
            'max_size_mb': 5,
            'min_days_old': 1,
            'nsfw': False
        },
        'moderate': {
            'type': ['.jpg', '.png', '.jpeg'],
            'max_size_mb': 10,
            'min_days_old': 0,
            'nsfw': False
        },
        'all': {
            'type': None,
            'max_size_mb': 50,
            'min_days_old': 0,
            'nsfw': True
        }
    }
    return presets.get(preset_name, config.DEFAULT_FILTERS.copy())