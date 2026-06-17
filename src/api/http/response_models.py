from math import ceil
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, computed_field


T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class Error(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    detail: Error


class DataResponse(BaseModel, Generic[T]):
    data: T


class Meta(BaseModel):
    page: int
    size: int
    total: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_pages(self) -> int:
        if self.total == 0:
            return 0
        return ceil(self.total / self.size)


class DataManyResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: Meta


class CommonResponse(BaseModel, Generic[T]):
    message: Optional[str] = None
    detail: Optional[Error] = None
    data: Optional[T] = None
