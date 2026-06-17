from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class BookingCreateInput:
    name: str
    scheduled_at: datetime
    service_type: str
