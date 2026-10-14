"""Общая настройка pytest для проекта «Генератор случайных цитат».

Добавляет каталог src в пути импорта, чтобы тесты могли обращаться
к модулям проекта напрямую: from modules.quote_storage import QuoteStorage.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
