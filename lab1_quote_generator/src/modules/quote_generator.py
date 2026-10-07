"""Модуль № 2. Генератор цитат: случайный выбор цитаты из готового списка.

Модуль полностью изолирован: он не знает о файлах и других модулях
проекта. На вход он получает список цитат (результат работы Модуля № 1),
на выход отдаёт одну случайную цитату — словарь {"text": ..., "category": ...}.
"""

import random

DEFAULT_CATEGORY = "Без категории"


class QuoteGenerator:
    """Выбирает случайную цитату из списка, в том числе по категории."""

    def __init__(self, quotes):
        if not quotes:
            raise ValueError("Список цитат пуст: выбирать не из чего")
        self.quotes = list(quotes)

    def random_quote(self, category=None):
        """Вернуть случайную цитату.

        Если указана категория — выбор идёт только среди цитат этой
        категории. Если подходящих цитат нет, поднимается ValueError.
        """
        pool = self.filter_by_category(category)
        if not pool:
            raise ValueError(f"Нет цитат в категории «{category}»")
        return random.choice(pool)

    def filter_by_category(self, category=None):
        """Вернуть список цитат указанной категории (или все цитаты)."""
        if not category:
            return list(self.quotes)
        return [quote for quote in self.quotes
                if quote.get("category") == category]

    def categories(self):
        """Вернуть отсортированный список категорий набора."""
        return sorted({quote.get("category", DEFAULT_CATEGORY)
                       for quote in self.quotes})
