from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import UUID, DateTime, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import BookingStatus

from .base import Base


class BookingModel(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status"),
        nullable=False,
        default=BookingStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (Index("idx_bookings_status", "status"),)
