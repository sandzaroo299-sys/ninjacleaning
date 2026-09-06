"""
Pydantic-схемы.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class UserOut(BaseModel):
    id: int
    telegram_id: int
    full_name: Optional[str] = None
    role: str
    apartment_id: Optional[int] = None
    class Config:
        from_attributes = True

class BuildingOut(BaseModel):
    id: int
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    facade_angle: Optional[float] = None
    entrances_count: int
    floors_count: int
    class Config:
        from_attributes = True

class ApartmentOut(BaseModel):
    id: int
    building_id: int
    entrance: int
    floor: int
    number: str
    window_side: str
    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    building_id: int
    apartment_number: str
    full_name: Optional[str] = None
    window_side: Optional[str] = "unknown"

class RegisterResponse(BaseModel):
    user: UserOut
    apartment: ApartmentOut

class RequestCreate(BaseModel):
    service_type: str = Field(..., description="windows, balcony, both")
    comment: Optional[str] = None
    planned_date: Optional[datetime] = None

class RequestOut(BaseModel):
    id: int
    apartment_id: int
    user_id: int
    service_type: str
    status: str
    comment: Optional[str] = None
    planned_date: Optional[datetime] = None
    parent_request_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    apartment: Optional[ApartmentOut] = None
    user: Optional[UserOut] = None
    class Config:
        from_attributes = True

class RequestStatusUpdate(BaseModel):
    status: str = Field(..., description="new, in_progress, completed, paid, cancelled, urgent, completed_second, rejected")
    comment: Optional[str] = None

class ComplaintCreate(BaseModel):
    request_id: int
    comment: str = Field(..., min_length=1)
    photos: Optional[List[str]] = None

class ComplaintOut(BaseModel):
    id: int
    parent_request_id: int
    comment: str
    status: str
    created_at: datetime

class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int]
    request_id: Optional[int]
    type: str
    message_text: str
    priority: str
    sent_at: Optional[datetime]
    is_sent: bool
    created_at: datetime
    class Config:
        from_attributes = True

class SettingOut(BaseModel):
    key: str
    value: str
    class Config:
        from_attributes = True

class SettingUpdate(BaseModel):
    key: str
    value: str

class SolarPositionOut(BaseModel):
    building_id: int
    date: datetime
    sunrise: datetime
    sunset: datetime
    current_azimuth: float
    current_elevation: float
    illuminated_side: str

class WeatherAlertOut(BaseModel):
    building_id: int
    wind_speed: float
    rain_probability: float
    temperature: float
    message: str
    recommended_action: str
