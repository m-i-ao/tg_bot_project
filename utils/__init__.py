# utils/__init__.py
from .filters import file_passes_filters
from .db import *  # если есть функции в db.py
from .download import download_channel_history
from .download import download_file
from .filters import file_passes_filters
from .download import download_file  # ← ДОБАВЬ ЭТУ СТРОКУ
from .download import download_channel_history  # ← ЕСЛИ ИСПОЛЬЗУЕТСЯ В admin.py