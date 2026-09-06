"""
Модели SQLAlchemy.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="resident")
    apartment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("apartments.id"), nullable=True)

    apartment: Mapped[Optional["Apartment"]] = relationship(back_populates="residents")
    requests: Mapped[list["Request"]] = relationship(back_populates="user")

class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    address: Mapped[str] = mapped_column(String(255), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    facade_angle: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    entrances_count: Mapped[int] = mapped_column(Integer, default=1)
    floors_count: Mapped[int] = mapped_column(Integer, default=1)

    apartments: Mapped[list["Apartment"]] = relationship(back_populates="building", cascade="all, delete-orphan")

class Apartment(Base):
    __tablename__ = "apartments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    entrance: Mapped[int] = mapped_column(Integer, default=1)
    floor: Mapped[int] = mapped_column(Integer, default=1)
    number: Mapped[str] = mapped_column(String(20))
    window_side: Mapped[str] = mapped_column(String(20), default="unknown")

    building: Mapped["Building"] = relationship(back_populates="apartments")
    residents: Mapped[list["User"]] = relationship(back_populates="apartment")
    requests: Mapped[list["Request"]] = relationship(back_populates="apartment")

class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    apartment_id: Mapped[int] = mapped_column(ForeignKey("apartments.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    service_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="new", index=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    planned_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    parent_request_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requests.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    apartment: Mapped["Apartment"] = relationship(back_populates="requests")
    user: Mapped["User"] = relationship(back_populates="requests")
    parent_request: Mapped[Optional["Request"]] = relationship(remote_side=[id], backref="child_requests")
    work_logs: Mapped[list["WorkLog"]] = relationship(back_populates="request", cascade="all, delete-orphan")
    photos: Mapped[list["ComplaintPhoto"]] = relationship(back_populates="request", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="request")

class WorkLog(Base):
    __tablename__ = "work_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100))
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    request: Mapped["Request"] = relationship(back_populates="work_logs")
    user: Mapped["User"] = relationship()

class ComplaintPhoto(Base):
    __tablename__ = "complaint_photos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), index=True)
    file_path: Mapped[str] = mapped_column(String(500))

    request: Mapped["Request"] = relationship(back_populates="photos")

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    request_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requests.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(50))
    message_text: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[Optional["User"]] = relationship()
    request: Mapped[Optional["Request"]] = relationship(back_populates="notifications")

class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
