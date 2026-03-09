from __future__ import annotations

from http import HTTPStatus

from park_py.error_handling import ApplicationError, ErrorCode


class ParkingRecordNotFoundError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code=ErrorCode.NOT_FOUND, status=HTTPStatus.NOT_FOUND)


class ParkingRecordConflictError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code=ErrorCode.CONFLICT, status=HTTPStatus.CONFLICT)
