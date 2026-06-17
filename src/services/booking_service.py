from typing import TYPE_CHECKING, Optional
import uuid

from domain.entities import Booking
from domain.enums import BookingStatus
from errors import NotFoundError, UnprocessableError
from infrastructure.celery.booking_producer import send_booking_to_processing
from infrastructure.postgres.db import managed_transaction
from infrastructure.postgres.repositories import BookingRepo
from libs.logger.custom_logger import get_logger
from workers.booking_tasks import process_booking_task


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from domain.dto import BookingCreateInput
    from domain.filters import BookingFilter


logger = get_logger(__name__)


class BookingService:
    def __init__(self, db_transaction_factory: "async_sessionmaker[AsyncSession]"):
        # Инверсия зависимостей IBookingRepo не использовалась намеренно (для простоты)
        self._db_transaction_factory = db_transaction_factory

    async def create(self, booking_inp: "BookingCreateInput") -> Booking:
        booking = Booking.create(
            name=booking_inp.name,
            scheduled_at=booking_inp.scheduled_at,
            service_type=booking_inp.service_type,
        )

        async with managed_transaction(self._db_transaction_factory) as t:
            booking_repo = BookingRepo(t)
            _ = await booking_repo.create(booking)

            try:
                _ = await send_booking_to_processing(booking.id)
                logger.info(
                    "Processing task queued. Booking ID (Task ID): %s", booking.id
                )
            except Exception as exc:
                logger.warning(
                    "Failed to queue processing for booking %s: %s", booking.id, str(exc)
                )

        return booking

    async def get_one(self, booking_id: uuid.UUID) -> Booking:
        async with managed_transaction(self._db_transaction_factory) as t:
            booking_repo = BookingRepo(t)

            booking = await booking_repo.get_one(booking_id)
            if not booking:
                raise NotFoundError(f"Booking {booking_id} not found")

            return booking

    async def get_all(
        self, filter: "BookingFilter", limit: int = 20, offset: Optional[int] = None
    ) -> tuple[list[Booking], int]:
        async with managed_transaction(self._db_transaction_factory) as t:
            booking_repo = BookingRepo(t)

            if count := await booking_repo.count():
                bookings = await booking_repo.get_all(filter, limit, offset)
                return bookings, count
            else:
                return [], 0

    async def cancel(self, booking_id: uuid.UUID):
        async with managed_transaction(self._db_transaction_factory) as t:
            booking_repo = BookingRepo(t)

            booking = await booking_repo.get_one(booking_id)
            if not booking:
                return  # Already cancelled (deleted)

            if booking.status != BookingStatus.PENDING:
                raise UnprocessableError("Only pending bookings can be cancelled")

            booking.cancel()

            # Отменённые записи удаляются (по ТЗ)
            await booking_repo.delete(booking_id)

            task_id = str(booking_id)

            _ = process_booking_task.app.control.revoke(task_id, terminate=True)

            logger.info("Task revoked and booking cancelled: %s", task_id)
