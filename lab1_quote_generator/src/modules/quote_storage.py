"""Модуль № 1. Хранилище цитат: загрузка и проверка данных из JSON-файла.

Модуль полностью изолирован: он не знает о других модулях проекта.
На вход он получает путь к файлу, на выход отдаёт список цитат —
список словарей вида {"text": "...", "category": "..."}.
"""

import json
from pathlib import Path

DEFAULT_CATEGORY = "Без категории"


class QuoteStorageError(Exception):
    """Ошибка чтения или разбора файла с цитатами."""


class QuoteStorage:
    """Загружает список цитат из JSON-файла и проверяет его структуру."""

    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        """Прочитать файл, проверить структуру и вернуть список цитат."""
        data = self._read_file()
        return self._parse(data)

    def _read_file(self):
        """Прочитать JSON-файл и вернуть его содержимое."""
        if not self.path.exists():
            raise QuoteStorageError(f"Файл с цитатами не найден: {self.path}")
        try:
            with self.path.open(encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as error:
            raise QuoteStorageError(
                f"Файл {self.path.name} содержит некорректный JSON: {error}"
            ) from error

    def _parse(self, data):
        """Проверить структуру данных и вернуть список корректных цитат."""
        if not isinstance(data, list):
            raise QuoteStorageError("Ожидался список цитат в формате JSON: [...]")
        quotes = [quote for quote in map(self._normalize, data) if quote]
        if not quotes:
            raise QuoteStorageError("В файле не найдено ни одной корректной цитаты")
        return quotes

    @staticmethod
    def _normalize(item):
        """Привести запись к виду {"text": ..., "category": ...}.

        Записи без текста и элементы, не являющиеся словарями,
        пропускаются — метод возвращает None.
        """
        if not isinstance(item, dict):
            return None
        text = str(item.get("text", "")).strip()
        if not text:
            return None
        category = str(item.get("category", DEFAULT_CATEGORY)).strip()
        return {"text": text, "category": category or DEFAULT_CATEGORY}
