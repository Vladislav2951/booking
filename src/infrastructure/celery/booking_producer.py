from typing import TYPE_CHECKING, Any

from celery.result import AsyncResult

from libs.logger.custom_logger import get_logger
from workers.booking_tasks import process_booking_task


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


def get_task_status(task_id: str) -> dict[str, Any]:
    try:
        result = AsyncResult(task_id, app=process_booking_task.app)  # type: ignore[var-annotated]

        if not result.ready():
            return {"status": "pending", "task_id": task_id}

        raw_result = None
        try:
            raw_result = result.result
        except Exception as e:
            logger.warning("Failed to read Celery result for %s: %s", task_id, e)

        if result.successful():
            base = {"status": "success", "task_id": task_id}
            return {**base, **raw_result} if isinstance(raw_result, dict) else base

        elif result.failed():
            error_msg = str(result.result) if hasattr(result, "result") else None
            return {
                "status": "failed",
                "task_id": task_id,
                "error": error_msg,
                "retries_exhausted": isinstance(raw_result, dict)
                and raw_result.get("retries_exhausted"),
            }

        elif result.state == "REVOKED" or (
            isinstance(result.result, str)
            and result.result.startswith("<SoftTimeLimitExceeded")
        ):
            return {"status": "revoked", "task_id": task_id}

    except Exception as e:
        logger.error("Error checking status for %s: %s", task_id, exc_info=e)

    return {
        "status": "unknown",
        "task_id": task_id,
        "message": "Result expired or backend unavailable",
    }
