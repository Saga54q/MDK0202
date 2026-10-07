"""Точка входа приложения «Генератор случайных цитат».

Связующий код: настройки → Модуль № 1 (хранилище) → Модуль № 2 (генератор)
→ интерфейс. Выходные данные Модуля № 1 автоматически передаются
на вход Модулю № 2.
"""

from pathlib import Path

from modules.config import load_config
from modules.quote_generator import QuoteGenerator
from modules.quote_storage import QuoteStorage
from modules.ui import UserInterface


def main():
    project_root = Path(__file__).resolve().parent.parent

    # Настройки приложения: путь к файлу цитат и категория для выбора
    config = load_config(project_root / "config.json")
    quotes_file = project_root / config["quotes_file"]

    # Модуль № 1: загрузка и проверка данных из файла
    storage = QuoteStorage(quotes_file)
    quotes = storage.load()

    # Модуль № 2: случайный выбор цитаты (при настройке — из категории)
    generator = QuoteGenerator(quotes)

    # Интерфейс: вывод результата пользователю
    ui = UserInterface(generator)
    ui.run(config.get("category"))


if __name__ == "__main__":
    main()
