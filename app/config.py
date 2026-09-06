"""
Конфигурация приложения.
"""

import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    BOT_TOKEN: str
    ADMIN_IDS: List[int]
    WORKER_IDS: List[int]
    MINI_APP_URL: str
    DATABASE_URL: str
    WEATHER_PROVIDER: str = "openmeteo"
    YANDEX_WEATHER_API_KEY: Optional[str] = None
    WIND_SPEED_THRESHOLD: float = 12.0
    RAIN_PROBABILITY_THRESHOLD: int = 50
    TEMPERATURE_THRESHOLD: float = 30.0
    WEATHER_CHECK_INTERVAL: int = 3600
    MAX_COMPLAINT_PHOTOS: int = 3

def _parse_ids(raw: str) -> List[int]:
    if not raw:
        return []
    try:
        return [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError:
        raise ValueError(f"Некорректный формат списка ID: {raw}")

def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise EnvironmentError("BOT_TOKEN не задан в .env файле")

    admin_ids_raw = os.getenv("ADMIN_IDS", "")
    worker_ids_raw = os.getenv("WORKER_IDS", "")

    mini_app_url = os.getenv("MINI_APP_URL", "")
    if not mini_app_url:
        raise EnvironmentError("MINI_APP_URL не задан в .env файле")

    database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    weather_provider = os.getenv("WEATHER_PROVIDER", "openmeteo").lower()
    if weather_provider not in ("openmeteo", "yandex"):
        weather_provider = "openmeteo"

    yandex_key = os.getenv("YANDEX_WEATHER_API_KEY")
    if weather_provider == "yandex" and not yandex_key:
        weather_provider = "openmeteo"

    return Settings(
        BOT_TOKEN=bot_token,
        ADMIN_IDS=_parse_ids(admin_ids_raw),
        WORKER_IDS=_parse_ids(worker_ids_raw),
        MINI_APP_URL=mini_app_url.rstrip("/"),
        DATABASE_URL=database_url,
        WEATHER_PROVIDER=weather_provider,
        YANDEX_WEATHER_API_KEY=yandex_key,
    )

settings = get_settings()
