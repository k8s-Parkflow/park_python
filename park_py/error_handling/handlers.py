from http import HTTPStatus

from django.http import HttpRequest, JsonResponse

from park_py.error_handling.error_codes import ErrorCode
from park_py.error_handling.responses import (
    build_error_response,
    build_internal_server_error_response,
)


def handler404(_request: HttpRequest, _exception: Exception) -> JsonResponse:
    return build_error_response(
        code=ErrorCode.NOT_FOUND,
        status=HTTPStatus.NOT_FOUND,
    )


def handler500(_request: HttpRequest) -> JsonResponse:
    return build_internal_server_error_response()
