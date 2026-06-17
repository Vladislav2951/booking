from infrastructure.postgres.db import async_session_factory
from services import BookingService


_booking_service = BookingService(async_session_factory)


def booking_srv() -> BookingService:
    return _booking_service
