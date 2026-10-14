"""Модуль интерфейса: взаимодействие с пользователем.

Получает готовый генератор цитат и выводит выбранную цитату в консоль.
"""


class UserInterface:
    """Печатает заголовок приложения и выбранную цитату."""

    def __init__(self, generator):
        self.generator = generator

    def run(self, category=None):
        """Вывести случайную цитату (при указании — из заданной категории)."""
        quote = self.generator.random_quote(category)

        print("Генератор случайных цитат")
        if quote.get("category"):
            print(f"Категория: {quote['category']}")
        print(quote["text"])
