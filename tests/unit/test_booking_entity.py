from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities.booking import Booking
from domain.enums import BookingStatus
from errors import UnprocessableError


class TestBookingEntity:
    def test_create_defaults_to_pending(self):
        booking = Booking.create(
            "Client Name", datetime.now(timezone.utc), "service_type"
        )

        assert isinstance(booking.id, UUID)
        assert booking.name == "Client Name"
        assert booking.status == BookingStatus.PENDING
        assert booking.service_type == "service_type"
        assert booking.created_at.tzinfo is not None
        assert booking.updated_at.tzinfo is not None

    @pytest.mark.parametrize("method_name", ["confirm", "cancel"])
    def test_unprocessable_when_not_pending(self, method_name):
        now = datetime.now(timezone.utc)
        booking = Booking(
            id=uuid7(),
            name="T",
            scheduled_at=now,
            service_type="S",
            status=BookingStatus.CONFIRMED,
            created_at=now,
            updated_at=now,
        )

        with pytest.raises(UnprocessableError):
            getattr(booking, method_name)()
