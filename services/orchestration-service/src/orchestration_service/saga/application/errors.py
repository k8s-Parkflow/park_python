from __future__ import annotations


class DownstreamError(Exception):
    def __init__(
        self,
        *,
        dependency: str,
        error_code: str,
        message: str,
        status: int,
    ) -> None:
        super().__init__(message)
        self.dependency = dependency
        self.error_code = error_code
        self.message = message
        self.status = status
