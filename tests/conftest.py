from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import ASGITransport, AsyncClient
import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from dependencies import booking_srv
from domain.entities import Booking
from domain.enums import BookingStatus
from infrastructure.postgres.repositories.booking_repo import BookingRepo
from main import app
from services import BookingService


@pytest.fixture(autouse=True)
def mock_celery_tasks():
    """Мок отправки задачи в Celery."""
    with patch(
        "services.booking_service.send_booking_to_processing", new_callable=AsyncMock
    ):
        yield


@pytest.fixture()
def pending_booking():
    test_id = uuid7()
    now = datetime.now(timezone.utc)
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)

    return Booking(
        id=test_id,
        name="Test Booking",
        scheduled_at=tomorrow,
        service_type="hostel",
        status=BookingStatus.PENDING,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture()
def repo_mock(pending_booking):
    mock = MagicMock(spec=BookingRepo)

    mock.create = AsyncMock(return_value=pending_booking)
    mock.get_one = AsyncMock(return_value=pending_booking)
    mock.get_all = AsyncMock(return_value=[pending_booking])
    mock.count = AsyncMock(return_value=1)
    mock.save = AsyncMock()
    mock.flush = AsyncMock()
    mock.delete = AsyncMock()

    return mock


@pytest.fixture()
async def client(repo_mock):
    """Создаёт тестовый клиент FastAPI с полностью замоканной БД."""

    class FakeTransaction:
        async def __aenter__(self) -> "FakeTransaction":
            return self

        async def __aexit__(self, exc_type, exc_tb):
            pass

        async def commit(self):
            pass

        async def rollback(self):
            pass

        async def close(self):
            pass

    mock_factory = MagicMock(return_value=FakeTransaction())

    service = BookingService(db_transaction_factory=mock_factory)

    with patch("services.booking_service.BookingRepo", return_value=repo_mock):
        app.dependency_overrides[booking_srv] = lambda: service

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac


@pytest.fixture(autouse=True)
def clear_app_overrides():
    yield
    app.dependency_overrides.clear()
