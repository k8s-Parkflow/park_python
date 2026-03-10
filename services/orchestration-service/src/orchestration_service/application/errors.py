from __future__ import annotations

from park_py.error_handling import ApplicationError
from park_py.error_handling.error_codes import serialize_error_code

from orchestration_service.clients.http import DownstreamHttpError


def build_error_payload(
    *,
    code,
    message: str = "",
    details: dict | None = None,
) -> dict:
    return {
        "error": {
            "code": serialize_error_code(code),
            "message": message,
            "details": details,
        }
    }


def raise_application_error_from_downstream(exc: DownstreamHttpError) -> None:
    error = exc.payload.get("error", {})
    raise ApplicationError(
        code=error.get("code", "application_error"),
        message=error.get("message", ""),
        status=exc.status_code,
        details=error.get("details"),
    ) from exc


def raise_application_error_from_payload(*, error_payload: dict, status_code: int) -> None:
    error = error_payload.get("error", {})
    raise ApplicationError(
        code=error.get("code", "application_error"),
        message=error.get("message", ""),
        status=status_code,
        details=error.get("details"),
    )
