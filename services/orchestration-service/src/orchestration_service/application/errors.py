from park_py.error_handling import ApplicationError

from orchestration_service.clients.http import DownstreamHttpError


def raise_application_error_from_downstream(exc: DownstreamHttpError) -> None:
    error = exc.payload.get("error", {})
    raise ApplicationError(
        code=error.get("code", "application_error"),
        message=error.get("message", ""),
        status=exc.status_code,
        details=error.get("details"),
    ) from exc

