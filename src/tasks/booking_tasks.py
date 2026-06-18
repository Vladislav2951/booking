import asyncio
from typing import TYPE_CHECKING, Any

from celery import Celery, Task

from config import settings
from domain.enums import BookingStatus
from errors import NotFoundError
from infrastructure.postgres.db import async_session_factory, managed_transaction_async
from infrastructure.postgres.repositories import BookingRepo
from libs.logger.custom_logger import get_logger


if TYPE_CHECKING:
    from uuid import UUID

    from celery import Task

logger = get_logger("booking_worker")


celery_app = Celery(
    "booking_worker",
    broker=settings.REDIS_URI,
    backend=settings.REDIS_URI,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)


async def _simulate_external_api_call(booking_id: "UUID"):
    import random

    await asyncio.sleep(3)

    if random.random() < 0.15:
        raise ConnectionError("Mock external service timeout")


@celery_app.task(
    bind=True,
    # autoretry_for=(ConnectionError,), # * celery-aio-pool не поддерживает autoretry
    soft_time_limit=10,
    retry_backoff=True,
)
async def process_booking_task(
    self: "Task[Any, Any]", booking_id: "UUID"
) -> dict[str, str]:
    logger.info("Processing task for booking %s", booking_id)

    try:
        async with managed_transaction_async(async_session_factory) as t:
            repo = BookingRepo(t)
            booking = await repo.get_one(booking_id)

            if not booking:
                raise NotFoundError(f"Booking {booking_id} not found")

            if booking.status != BookingStatus.PENDING:
                return {"status": booking.status.value}

            await _simulate_external_api_call(booking_id)

            booking.confirm()
            await repo.save(booking)

    except ConnectionError as e:
        logger.debug("Retries: %d", self.request.retries)

        # Если это последняя попытка
        if self.request.retries >= (self.max_retries or 0) - 1:
            async with managed_transaction_async(async_session_factory) as t:
                repo = BookingRepo(t)

                booking = await repo.get_one(booking_id)
                if booking and booking.status == BookingStatus.PENDING:
                    booking.set_failed()
                    await repo.save(booking)

            logger.warning(
                "Booking %s failed after exhausting retries (%d)",
                booking_id,
                self.request.retries,
            )
            raise e

        self.retry(max_retries=2, countdown=1)  # (celery-aio-pool)

    return {"status": BookingStatus.CONFIRMED.value}
