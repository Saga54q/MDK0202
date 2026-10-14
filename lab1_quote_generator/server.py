# -*- coding: utf-8 -*-
"""Локальный веб-сервер приложения «Генератор случайных цитат».

Лабораторная работа № 6: интерфейс пользователя для проверки средствами
инструментальной среды разработки (браузер + DevTools: Elements, Styles,
Device Mode, Network, Console).

Запуск:
    python server.py
Интерфейс открывается в браузере по адресу http://127.0.0.1:8000

API:
    GET  /api/categories            список категорий цитат        (200 OK)
    GET  /api/quote?category=...    случайная цитата              (200 OK / 400)
    POST /api/login                 вход по коду доступа          (200 OK / 400 / 401)
"""

import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
WEB_DIR = PROJECT_ROOT / "web"
sys.path.insert(0, str(SRC_DIR))

from modules.config import load_config               # noqa: E402
from modules.quote_generator import QuoteGenerator   # noqa: E402
from modules.quote_storage import QuoteStorage       # noqa: E402

HOST = "127.0.0.1"
PORT = 8000

# Демонстрационные учётные данные (только для учебной проверки авторизации).
# В реальном проекте такие значения хранятся в переменных окружения.
DEMO_PASSWORD = "quote2026"

NAME_PATTERN = re.compile(r"^[А-Яа-яЁёA-Za-z][А-Яа-яЁёA-Za-z\s\-]{1,19}$")

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


def validate_username(name):
    """Проверить имя пользователя. Возвращает (имя, ошибка)."""
    name = (name or "").strip()
    if not name:
        return None, "Введите имя пользователя"
    if not NAME_PATTERN.match(name):
        return None, ("Имя может содержать только буквы, пробел и дефис "
                      "(от 2 до 20 символов)")
    return name, None


class QuoteService:
    """Данные и логика приложения (используются модули № 1 и № 2)."""

    def __init__(self, project_root):
        config = load_config(project_root / "config.json")
        quotes_file = project_root / config["quotes_file"]
        self.quotes = QuoteStorage(quotes_file).load()   # Модуль № 1
        self.generator = QuoteGenerator(self.quotes)     # Модуль № 2

    def categories(self):
        return self.generator.categories()

    def random_quote(self, category=None):
        return self.generator.random_quote(category)


class QuoteHandler(BaseHTTPRequestHandler):
    """Обработчик запросов: статические файлы интерфейса и JSON-API."""

    server_version = "QuoteGeneratorWeb/1.0"
    service = None

    # ---------------------------------------------------------- служебное
    def log_message(self, template, *args):
        """Единый формат журнала в консоли сервера."""
        print("[%s] %s" % (self.log_date_time_string(), template % args))

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def _serve_static(self, route):
        if route in ("", "/"):
            route = "/index.html"
        relative = Path(unquote(route).lstrip("/"))
        if relative.is_absolute() or ".." in relative.parts:
            self._send_json(404, {"error": "Недопустимый путь"})
            return
        file_path = WEB_DIR / relative
        if not file_path.is_file():
            self._send_json(404, {"error": "Файл не найден"})
            return
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type",
                         CONTENT_TYPES.get(file_path.suffix,
                                           "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ------------------------------------------------------------- маршруты
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/categories":
            self._send_json(200, {"categories": self.service.categories()})
            return
        if parsed.path == "/api/quote":
            category = (parse_qs(parsed.query).get("category") or [""])[0].strip()
            try:
                quote = self.service.random_quote(category or None)
            except ValueError as error:
                self._send_json(400, {"error": str(error)})
                return
            self._send_json(200, {"quote": quote})
            return
        self._serve_static(parsed.path)

    def do_POST(self):
        if urlparse(self.path).path != "/api/login":
            self._send_json(404, {"error": "Неизвестный метод API"})
            return
        data = self._read_json_body()
        if data is None:
            self._send_json(400, {"error": "Тело запроса должно быть в формате JSON"})
            return
        username, error = validate_username(data.get("username"))
        if error:
            self._send_json(400, {"error": error})
            return
        password = str(data.get("password") or "")
        if not password:
            self._send_json(400, {"error": "Введите код доступа"})
            return
        if password != DEMO_PASSWORD:
            self._send_json(401, {"error": "Неверный код доступа"})
            return
        self._send_json(200, {"user": username, "message": "Вход выполнен"})


def main():
    QuoteHandler.service = QuoteService(PROJECT_ROOT)
    server = ThreadingHTTPServer((HOST, PORT), QuoteHandler)
    print("Генератор случайных цитат — локальный веб-сервер")
    print(f"Адрес: http://{HOST}:{PORT}")
    print(f"Демонстрационный код доступа: {DEMO_PASSWORD}")
    print(f"Категории: {', '.join(QuoteHandler.service.categories())}")
    print("Остановка сервера: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
