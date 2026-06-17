import asyncio
from datetime import timezone
from typing import TYPE_CHECKING

from celery import Celery

from config import settings
from domain.enums import BookingStatus
from errors import NotFoundError
from infrastructure.postgres.db import async_session_factory, managed_transaction
from infrastructure.postgres.repositories import BookingRepo
from libs.logger.custom_logger import get_logger


if TYPE_CHECKING:
    from uuid import UUID

logger = get_logger("booking_worker")


celery_app = Celery(
    "booking_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)

# celery_app.conf.update(

# )


async def _simulate_external_api_call(booking_id: "UUID"):
    import random

    await asyncio.sleep(1)

    if random.random() < 0.15:
        raise ConnectionError("Mock external service timeout")


@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    max_retries=2,
    soft_time_limit=10,
)
def process_booking_task(self, booking_id: "UUID") -> dict[str, str]:
    logger.info("Processing task for booking %s", booking_id)

    async def _run_async() -> dict[str, str]:
        try:
            async with managed_transaction(async_session_factory) as t:
                repo = BookingRepo(t)
                booking = await repo.get_one(booking_id)

                if not booking:
                    raise NotFoundError(f"Booking {booking_id} not found")

                if booking.status != BookingStatus.PENDING:
                    return {"status": booking.status.value}

                await _simulate_external_api_call(booking_id)

                booking.confirm()
                await repo.save(booking)
                return {"status": BookingStatus.CONFIRMED.value}

        except ConnectionError as e:
            # Если это последняя попытка
            if self.request.retries >= self.max_retries - 1:
                async with managed_transaction(async_session_factory) as t:
                    repo = BookingRepo(t)

                    booking = await repo.get_one(booking_id)
                    if booking and booking.status == BookingStatus.PENDING:
                        booking.set_failed()
                        await repo.save(booking)

                logger.warning("Booking %s failed after exhausting retries", booking_id)

            raise e  # retry

    try:
        return asyncio.run(_run_async())
    except ConnectionError as e:
        # Исключение после исчерпания всех попыток
        logger.exception("Booking %s failed after retries: %s", booking_id, e)
        return {"status": BookingStatus.FAILED.value}
