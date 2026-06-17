from abc import ABC
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo(ABC):
    def __init__(self, session: "AsyncSession"):
        self._session = session
