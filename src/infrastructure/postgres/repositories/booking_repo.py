from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import delete, func, select, update

from domain.entities import Booking
from infrastructure.postgres.models import BookingModel
from libs.logger.custom_logger import get_logger

from .base_repo import BaseRepo


if TYPE_CHECKING:
    from domain.filters import BookingFilter


logger = get_logger(__name__)


class BookingRepo(BaseRepo):
    async def create(self, booking: Booking) -> Booking:
        new_booking = BookingModel(
            id=booking.id,
            name=booking.name,
            scheduled_at=booking.scheduled_at,
            status=booking.status,
            service_type=booking.service_type,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )

        self._session.add(new_booking)
        await self._session.flush()

        return _to_domain(new_booking)

    async def get_one(self, booking_id: uuid.UUID) -> Optional[Booking]:
        stmt = select(BookingModel).where(BookingModel.id == booking_id)

        result = await self._session.execute(stmt)

        model = result.scalar_one_or_none()
        if not model:
            return None

        return _to_domain(model)

    async def get_all(
        self,
        filter: Optional["BookingFilter"] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Booking]:
        stmt = select(BookingModel)

        if filter and filter.statuses:
            stmt = stmt.where(BookingModel.status.in_(filter.statuses))

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)

        models = result.scalars().all()
        if not models:
            return []

        return [_to_domain(el) for el in models]

    async def count(self) -> int:
        stmt = select(func.count()).select_from(BookingModel)
        total_result = await self._session.execute(stmt)
        return total_result.scalar_one()

    # async def update(
    #     self, booking_id: uuid.UUID, update_inp: BookingUpdateInput
    # ) -> Booking:
    #     to_update = update_inp.model_dump(exclude_unset=True)

    #     if not to_update:
    #         raise UpdateError(f"Nothing to update for {booking_id}")

    #     stmt = (
    #         update(BookingModel)
    #         .where(BookingModel.id == booking_id)
    #         .values(**to_update)
    #         .returning(BookingModel)
    #     )

    #     result = await self.__session.execute(stmt)
    #     model = result.scalar_one()

    #     return Booking.model_validate(model)

    async def save(self, booking: Booking) -> Booking:
        stmt = (
            update(BookingModel)
            .where(BookingModel.id == booking.id)
            .values(
                name=booking.name,
                scheduled_at=booking.scheduled_at,
                status=booking.status,
                service_type=booking.service_type,
                updated_at=booking.updated_at,
            )
            .returning(BookingModel)
        )

        result = await self._session.execute(stmt)

        model = result.scalar_one()

        return _to_domain(model)

    async def delete(self, id: uuid.UUID):
        stmt = delete(BookingModel).where(BookingModel.id == id)
        await self._session.execute(stmt)


def _to_domain(model: BookingModel) -> Booking:
    return Booking(
        id=model.id,
        name=model.name,
        scheduled_at=model.scheduled_at,
        status=model.status,
        service_type=model.service_type,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
