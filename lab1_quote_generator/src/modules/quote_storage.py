"""Модуль № 1. Хранилище цитат: загрузка и проверка данных из JSON-файла.

Модуль полностью изолирован: он не знает о других модулях проекта.
На вход он получает путь к файлу, на выход отдаёт список цитат —
список словарей вида {"text": "...", "category": "..."}.
"""

import json
import logging
from pathlib import Path

DEFAULT_CATEGORY = "Без категории"

logger = logging.getLogger(__name__)


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

        logger.info("Загружено цитат: %d из %d записей", len(quotes), len(data))
        if not quotes:
            raise QuoteStorageError("В файле не найдено ни одной корректной цитаты")
        return quotes

    @classmethod
    def _normalize(cls, item):
        """Привести запись к виду {"text": ..., "category": ...}.

        Записи без текста и элементы, не являющиеся словарями,
        пропускаются — метод возвращает None.

        Поля проверяются по типу: значение null или число не должно
        превращаться в строку «None» или «42» (ошибка, найденная
        при отладке в лабораторной работе № 5).
        """
        if not isinstance(item, dict):
            logger.warning("Пропущена запись, не являющаяся объектом: %r", item)
            return None

        raw_text = item.get("text")
        if not isinstance(raw_text, str) or not raw_text.strip():
            logger.warning("Пропущена запись без текста: %r", item)
            return None

        raw_category = item.get("category")
        if not isinstance(raw_category, str) or not raw_category.strip():
            logger.warning(
                "Категория не указана или не является строкой, "
                "использовано значение по умолчанию: %r", item
            )
            raw_category = DEFAULT_CATEGORY

        return {"text": raw_text.strip(), "category": raw_category.strip()}
