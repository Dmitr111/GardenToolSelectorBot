"""Конфигурация бота: значения читаются из переменных окружения / файла .env."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# .env лежит в корне репозитория
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        sys.exit(
            f"Ошибка конфигурации: не задана обязательная переменная окружения {name}.\n"
            "Скопируйте .env.example в .env и заполните значения."
        )
    return value


def _parse_admin_ids(raw: str) -> list[int]:
    try:
        return [int(part) for part in raw.split(",") if part.strip()]
    except ValueError:
        sys.exit("Ошибка конфигурации: ADMIN_IDS должен содержать числовые Telegram ID через запятую.")


TOKEN = _require("BOT_TOKEN")
CONNECTIONSTRING = _require("DATABASE_URL")
ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))
