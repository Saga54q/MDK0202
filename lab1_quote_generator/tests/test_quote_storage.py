"""Модульные тесты Модуля № 1 (хранилище цитат)."""

import json

import pytest

from modules.quote_storage import DEFAULT_CATEGORY, QuoteStorage, QuoteStorageError


@pytest.fixture
def make_file(tmp_path):
    """Создать временный файл с переданным содержимым."""

    def create(content, name="quotes.json"):
        path = tmp_path / name
        if isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            path.write_text(
                json.dumps(content, ensure_ascii=False), encoding="utf-8"
            )
        return path

    return create


def test_load_returns_all_quotes(make_file):
    """Корректный файл: все цитаты загружаются с текстом и категорией."""
    path = make_file([
        {"text": "Первая цитата", "category": "Мотивация"},
        {"text": "Вторая цитата", "category": "Учёба"},
    ])

    quotes = QuoteStorage(path).load()

    assert len(quotes) == 2
    assert quotes[0] == {"text": "Первая цитата", "category": "Мотивация"}
    assert quotes[1]["category"] == "Учёба"


def test_category_defaults_to_base_value(make_file):
    """Если категория не указана, подставляется значение по умолчанию."""
    path = make_file([{"text": "Цитата без категории"}])

    quotes = QuoteStorage(path).load()

    assert quotes[0]["category"] == DEFAULT_CATEGORY


def test_records_without_text_are_skipped(make_file):
    """Записи без текста и элементы не-словари пропускаются."""
    path = make_file([
        {"text": "Правильная цитата"},
        {"category": "Без текста"},
        {"text": "   "},
        "строка вместо объекта",
        42,
    ])

    quotes = QuoteStorage(path).load()

    assert len(quotes) == 1
    assert quotes[0]["text"] == "Правильная цитата"


def test_text_is_trimmed(make_file):
    """Лишние пробелы вокруг текста и категории удаляются."""
    path = make_file([{"text": "  Цитата с пробелами  ", "category": " Тест "}])

    quotes = QuoteStorage(path).load()

    assert quotes[0]["text"] == "Цитата с пробелами"
    assert quotes[0]["category"] == "Тест"


def test_missing_file_raises_error(tmp_path):
    """Отсутствующий файл приводит к понятной ошибке."""
    with pytest.raises(QuoteStorageError, match="не найден"):
        QuoteStorage(tmp_path / "no_such_file.json").load()


def test_broken_json_raises_error(make_file):
    """Некорректный JSON приводит к понятной ошибке."""
    path = make_file("{ это не JSON }")

    with pytest.raises(QuoteStorageError, match="некорректный JSON"):
        QuoteStorage(path).load()


def test_not_a_list_raises_error(make_file):
    """Если в файле не список, поднимается ошибка структуры."""
    path = make_file({"text": "Объект вместо списка"})

    with pytest.raises(QuoteStorageError, match="Ожидался список"):
        QuoteStorage(path).load()


def test_empty_result_raises_error(make_file):
    """Если корректных цитат нет, поднимается ошибка."""
    path = make_file([{"category": "Без текста"}])

    with pytest.raises(QuoteStorageError, match="ни одной корректной цитаты"):
        QuoteStorage(path).load()
