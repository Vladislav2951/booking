from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Self
from uuid import UUID

from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.errors import UnprocessableError


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Booking:
    id: UUID
    name: str
    scheduled_at: datetime
    service_type: str
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str, scheduled_at: datetime, service_type: datetime) -> Self:
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid7(),
            name=name,
            scheduled_at=scheduled_at,
            service_type=service_type,
            status=BookingStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    def confirm(self):
        if self.status != BookingStatus.PENDING:
            raise UnprocessableError(
                f"Only pending bookings can be confirmed; current status: {self.status.value}"
            )

        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.now(timezone.utc)

    def cancel(self):
        if self.status != BookingStatus.PENDING:
            raise UnprocessableError(
                f"Only pending bookings can be cancelled; current status: {self.status.value}"
            )

        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc)
