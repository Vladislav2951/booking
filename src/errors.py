from typing import Optional


class AppError(Exception):
    def __init__(self, message: Optional[str] = None):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message)


class UnprocessableError(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message)
