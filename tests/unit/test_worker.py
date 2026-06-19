from unittest.mock import MagicMock, patch

from tasks.booking_tasks import on_booking_task_failure, on_booking_task_success


class TestWorkerSignals:
    def test_on_booking_task_success(self):
        sender = MagicMock()
        sender.request.args = ("test-booking-id",)
        result_data = {"status": "confirmed"}

        with patch("tasks.booking_tasks.logger") as mock_logger:
            on_booking_task_success(sender=sender, result=result_data)

            log_msg = str(mock_logger.info.call_args[0][0])
            assert "[MOCK] Уведомление отправлено:" in log_msg
            assert "booking.completed" in log_msg

    def test_on_booking_task_failure(self):
        sender = MagicMock()
        sender.request.args = ("another-booking-id",)
        exc = ConnectionError("Service timeout")

        with patch("tasks.booking_tasks.logger") as mock_logger:
            on_booking_task_failure(sender=sender, exception=exc)

            log_msg = str(mock_logger.warning.call_args[0][0])
            assert "[MOCK] Уведомление об ошибке:" in log_msg
            assert "booking.failed" in log_msg

    def test_signal_handlers_missing_or_empty_args(self):
        sender = MagicMock()
        sender.request.args = ()  # Пустой кортеж -> booking_id="unknown"

        with patch("tasks.booking_tasks.logger") as mock_logger:
            on_booking_task_success(sender=sender, result={"status": "ok"})

            log_msg = str(mock_logger.info.call_args[0][0])
            assert "[MOCK] Уведомление отправлено:" in log_msg
