"""Модульные тесты Модуля № 2 (генератор цитат)."""

import pytest

from modules.quote_generator import QuoteGenerator

QUOTES = [
    {"text": "Раз", "category": "Мотивация"},
    {"text": "Два", "category": "Мотивация"},
    {"text": "Три", "category": "Учёба"},
]


def test_random_quote_returns_item_from_list():
    """Случайный выбор всегда возвращает цитату из переданного списка."""
    generator = QuoteGenerator(QUOTES)

    for _ in range(20):
        assert generator.random_quote() in QUOTES


def test_random_quote_uses_different_items():
    """Из набора из нескольких цитат выбираются разные (проверка случайности)."""
    generator = QuoteGenerator(QUOTES)

    results = {generator.random_quote()["text"] for _ in range(50)}

    assert len(results) > 1


def test_random_quote_filters_by_category():
    """При указании категории выбираются только её цитаты."""
    generator = QuoteGenerator(QUOTES)

    for _ in range(20):
        quote = generator.random_quote("Учёба")
        assert quote["category"] == "Учёба"


def test_filter_by_category_returns_only_its_quotes():
    """filter_by_category возвращает цитаты только нужной категории."""
    generator = QuoteGenerator(QUOTES)

    assert generator.filter_by_category("Мотивация") == QUOTES[:2]
    assert generator.filter_by_category() == QUOTES


def test_unknown_category_raises_error():
    """Несуществующая категория приводит к понятной ошибке."""
    generator = QuoteGenerator(QUOTES)

    with pytest.raises(ValueError, match="Нет цитат в категории"):
        generator.random_quote("Спорт")


def test_categories_are_sorted_and_unique():
    """Список категорий отсортирован и не содержит повторов."""
    generator = QuoteGenerator(QUOTES)

    assert generator.categories() == ["Мотивация", "Учёба"]


def test_empty_list_raises_error():
    """Пустой список цитат создавать нельзя."""
    with pytest.raises(ValueError, match="Список цитат пуст"):
        QuoteGenerator([])


def test_source_list_is_not_modified():
    """Генератор копирует список и не меняет исходные данные."""
    generator = QuoteGenerator(QUOTES)

    generator.random_quote("Учёба")

    assert generator.quotes == QUOTES
