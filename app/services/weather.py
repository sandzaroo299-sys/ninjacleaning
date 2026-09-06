"""
Сервис погоды (Open-Meteo бесплатный).
"""

import asyncio
from typing import Optional

import aiohttp

from app.config import settings
from app.models import Building

async def fetch_openmeteo_weather(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,precipitation_probability",
        "hourly": "temperature_2m,wind_speed_10m,precipitation_probability",
        "forecast_days": 2,
        "timezone": "auto",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

def _extract_openmeteo(data: dict, hours_offset: int = 0) -> dict:
    current = data.get("current", {})
    hourly = data.get("hourly", {})
    if hours_offset == 0:
        return {
            "temperature": current.get("temperature_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "precipitation_probability": current.get("precipitation_probability"),
        }
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    winds = hourly.get("wind_speed_10m", [])
    precips = hourly.get("precipitation_probability", [])
    if hours_offset < len(temps):
        return {
            "temperature": temps[hours_offset],
            "wind_speed": winds[hours_offset],
            "precipitation_probability": precips[hours_offset],
        }
    return {}

async def _get_weather_for_coords(lat: float, lon: float, hours_offset: int = 0) -> dict:
    if not lat or not lon:
        return {}
    try:
        data = await fetch_openmeteo_weather(lat, lon)
        return _extract_openmeteo(data, hours_offset)
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
        return {}

def check_thresholds(weather: dict) -> Optional[str]:
    warnings = []
    wind = weather.get("wind_speed")
    temp = weather.get("temperature")
    precip = weather.get("precipitation_probability")
    if wind is not None and wind > settings.WIND_SPEED_THRESHOLD:
        warnings.append(f"Ветер {wind:.1f} м/с (порог {settings.WIND_SPEED_THRESHOLD} м/с)")
    if temp is not None and temp > settings.TEMPERATURE_THRESHOLD:
        warnings.append(f"Температура {temp:.1f}°C (порог {settings.TEMPERATURE_THRESHOLD}°C)")
    if precip is not None and precip > settings.RAIN_PROBABILITY_THRESHOLD:
        warnings.append(f"Вероятность дождя {precip}% (порог {settings.RAIN_PROBABILITY_THRESHOLD}%)")
    if warnings:
        return "⚠️ Неблагоприятные условия: " + ", ".join(warnings) + ". Рекомендуется перенести работы."
    return None

def get_weather_alert_for_building(building: Building) -> dict:
    if not building.latitude or not building.longitude:
        return {
            "building_id": building.id,
            "wind_speed": 0,
            "rain_probability": 0,
            "temperature": 0,
            "message": "Нет координат для здания",
            "recommended_action": "Добавьте координаты",
        }
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    weather = loop.run_until_complete(_get_weather_for_coords(building.latitude, building.longitude, 0))
    loop.close()
    message = check_thresholds(weather)
    return {
        "building_id": building.id,
        "wind_speed": weather.get("wind_speed", 0),
        "rain_probability": weather.get("precipitation_probability", 0),
        "temperature": weather.get("temperature", 0),
        "message": message or "Погода в норме",
        "recommended_action": "Перенесите работы" if message else "Можно работать",
    }
