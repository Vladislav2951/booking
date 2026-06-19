from datetime import datetime
from typing import Optional

from pydantic import UUID7, BaseModel, ConfigDict, Field

from domain.enums import BookingStatus

from .common_schemas import Pagination


class BookingCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scheduled_at: datetime = Field(alias="datetime")
    service_type: str = Field(min_length=1, max_length=50)


class BookingGetAllSchema(Pagination):
    statuses: Optional[set[BookingStatus]] = None


class BookingResponseSchema(BaseModel):
    id: UUID7
    name: str
    scheduled_at: datetime = Field(serialization_alias="datetime")
    service_type: str
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)
