from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import path

from park_py.error_handling import ApplicationError
from park_py.error_handling import ErrorCode
from park_py.error_handling import handler404 as json_handler404
from park_py.error_handling import handler500 as json_handler500


def raise_application_error(_request: HttpRequest) -> HttpResponse:
    raise ApplicationError(
        code=ErrorCode.CONFLICT,
        status=409,
        details={"reason": "이미 처리된 요청입니다."},
    )


def raise_validation_error(_request: HttpRequest) -> HttpResponse:
    raise ValidationError({"field": ["필수 입력값입니다."]})


def raise_permission_denied(_request: HttpRequest) -> HttpResponse:
    raise PermissionDenied("권한이 없습니다.")


def raise_runtime_error(_request: HttpRequest) -> HttpResponse:
    raise RuntimeError("unexpected failure")


urlpatterns = [
    path("test-errors/application/", raise_application_error),
    path("test-errors/validation/", raise_validation_error),
    path("test-errors/permission/", raise_permission_denied),
    path("test-errors/runtime/", raise_runtime_error),
]

handler404 = json_handler404
handler500 = json_handler500
