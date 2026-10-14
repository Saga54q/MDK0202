"""Сценарий отладки Модуля № 1 «Парсер данных».

Запуск в PyCharm: правый клик по файлу → Debug 'debug_demo'.
Точка останова (breakpoint) ставится в файле
src/modules/quote_storage.py в методе _normalize — на строке,
где значение поля text переводится в строку:

    text = str(item.get("text", "")).strip()

Данные с ошибками берутся из файла data/quotes_bad.json.
"""

import logging
from pathlib import Path

from modules.quote_generator import QuoteGenerator
from modules.quote_storage import QuoteStorage


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    project_root = Path(__file__).resolve().parent.parent
    bad_file = project_root / "data" / "quotes_bad.json"

    print(f"Файл с данными: {bad_file.name}")
    storage = QuoteStorage(bad_file)
    quotes = storage.load()

    print(f"\nЗагружено цитат: {len(quotes)}")
    for quote in quotes:
        print(f"  text={quote['text']!r}   category={quote['category']!r}")

    generator = QuoteGenerator(quotes)
    print("\nСлучайная цитата:", generator.random_quote()["text"])


if __name__ == "__main__":
    main()
