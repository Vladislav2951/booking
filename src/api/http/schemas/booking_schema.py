from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field

from domain.enums import BookingStatus

from .common_schemas import Pagination


class BookingCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scheduled_at: datetime = Field(alias="datetime")
    service_type: str = Field(min_length=1, max_length=50)


class BookingGetAllSchema(Pagination):
    statuses: Optional[set[BookingStatus]]


class BookingResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    scheduled_at: datetime = Field(serialization_alias="datetime")
    service_type: str
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)


class PaginatedBookings(BaseModel):
    items: list[BookingResponseSchema]
    total: int
    page: int
    size: int
