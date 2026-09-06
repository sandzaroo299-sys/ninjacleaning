"""
Солнечное планирование (без pytz).
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from astral import LocationInfo
from astral.sun import sun, elevation, azimuth

from app.models import Building

def _get_location(building: Building) -> Optional[LocationInfo]:
    if not building.latitude or not building.longitude:
        return None
    return LocationInfo(
        name="building",
        region="",
        timezone="UTC",
        latitude=building.latitude,
        longitude=building.longitude,
    )

def _get_sun_times(building: Building, date: datetime) -> Optional[dict]:
    location = _get_location(building)
    if not location:
        return None
    day = date.date()
    try:
        return sun(location.observer, date=day)
    except Exception:
        return None

def _calculate_solar_position(building: Building, date: datetime) -> Optional[Tuple[float, float]]:
    location = _get_location(building)
    if not location:
        return None
    try:
        elev = elevation(location.observer, date)
        azim = azimuth(location.observer, date)
        return azim, elev
    except Exception:
        return None

def determine_illuminated_side(azimuth: float, building: Building) -> str:
    azimuth = azimuth % 360
    if 315 <= azimuth or azimuth < 45:
        return "north"
    elif 45 <= azimuth < 135:
        return "east"
    elif 135 <= azimuth < 225:
        return "south"
    elif 225 <= azimuth < 315:
        return "west"
    return "unknown"

def get_solar_position_for_building(building: Building) -> dict:
    now = datetime.utcnow()
    sun_times = _get_sun_times(building, now)
    sunrise = sun_times["sunrise"] if sun_times else None
    sunset = sun_times["sunset"] if sun_times else None
    position = _calculate_solar_position(building, now)
    azimuth, elevation_val = position if position else (0, 0)
    illuminated_side = determine_illuminated_side(azimuth, building)
    return {
        "building_id": building.id,
        "date": now,
        "sunrise": sunrise,
        "sunset": sunset,
        "current_azimuth": azimuth,
        "current_elevation": elevation_val,
        "illuminated_side": illuminated_side,
    }

def generate_daily_plan(building: Building) -> list:
    plan = []
    now = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0)
    periods = [
        ("morning", now, now + timedelta(hours=4)),
        ("afternoon", now + timedelta(hours=4), now + timedelta(hours=8)),
        ("evening", now + timedelta(hours=8), now + timedelta(hours=12)),
    ]
    for period_name, start, end in periods:
        mid_time = start + (end - start) / 2
        position = _calculate_solar_position(building, mid_time)
        if position:
            azimuth, _ = position
            side = determine_illuminated_side(azimuth, building)
            plan.append({
                "period": period_name,
                "start": start,
                "end": end,
                "illuminated_side": side,
                "recommendation": f"Работать на теневой стороне (противоположной {side})",
            })
        else:
            plan.append({
                "period": period_name,
                "start": start,
                "end": end,
                "illuminated_side": "unknown",
                "recommendation": "Нет данных",
            })
    return plan
