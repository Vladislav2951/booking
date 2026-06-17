from dataclasses import dataclass
from typing import Optional

from domain.enums import BookingStatus


@dataclass(slots=True)
class BookingFilter:
    statuses: Optional[set[BookingStatus]]
