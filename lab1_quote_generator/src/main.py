from pathlib import Path

from modules.quote_generator import QuoteGenerator
from modules.quote_storage import QuoteStorage
from modules.ui import UserInterface


def main():
    # Получаем путь к корню проекта
    project_root = Path(__file__).resolve().parent.parent

    # Формируем правильный путь к файлу с цитатами
    quotes_file = project_root / "data" / "quotes.json"

    storage = QuoteStorage(quotes_file)
    generator = QuoteGenerator(storage.load())
    ui = UserInterface(generator)

    ui.run()


if __name__ == "__main__":
    main()