from typing import TYPE_CHECKING

from libs.logger.custom_logger import get_logger
from tasks.booking_tasks import process_booking_task


if TYPE_CHECKING:
    from uuid import UUID


logger = get_logger("booking_producer")


async def send_booking_to_processing(booking_id: "UUID") -> str:
    try:
        result = process_booking_task.apply_async(
            args=(booking_id,), task_id=str(booking_id), expires=300  # 5 мин
        )

        return result.id

    except Exception as ex:
        raise RuntimeError(f"Failed to queue processing for booking {booking_id}") from ex
