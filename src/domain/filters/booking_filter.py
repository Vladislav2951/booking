from domain.entities import BookingStatus


class BookingFilter:
    statuses: set[BookingStatus]
