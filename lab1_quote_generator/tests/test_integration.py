"""Интеграционный тест: сквозной сценарий от файла с данными
до готовой цитаты (Модуль № 1 → Модуль № 2).
"""

from modules.quote_generator import QuoteGenerator
from modules.quote_storage import QuoteStorage


def test_scenario_from_file_to_quote(tmp_path):
    """Выходные данные Модуля № 1 передаются на вход Модулю № 2."""
    quotes_file = tmp_path / "quotes.json"
    quotes_file.write_text(
        '[{"text": "Сквозная проверка", "category": "Тест"}]',
        encoding="utf-8",
    )

    quotes = QuoteStorage(quotes_file).load()   # Модуль № 1
    generator = QuoteGenerator(quotes)          # Модуль № 2
    quote = generator.random_quote("Тест")

    assert quote == {"text": "Сквозная проверка", "category": "Тест"}


def test_scenario_with_project_data():
    """Сквозной сценарий на реальном файле проекта data/quotes.json."""
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    quotes = QuoteStorage(root / "data" / "quotes.json").load()
    generator = QuoteGenerator(quotes)

    quote = generator.random_quote()
    categories = generator.categories()

    assert quote["text"] in [item["text"] for item in quotes]
    assert "Мотивация" in categories
