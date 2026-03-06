import logging
from http import HTTPStatus

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpRequest
from django.http.response import HttpResponseBase
from django.utils.deprecation import MiddlewareMixin

from park_py.error_handling.error_codes import ErrorCode
from park_py.error_handling.exceptions import ApplicationError
from park_py.error_handling.responses import (
    build_error_response,
    build_internal_server_error_response,
    extract_validation_details,
)

logger = logging.getLogger(__name__)


class ExceptionHandlingMiddleware(MiddlewareMixin):
    def process_exception(self, _request: HttpRequest, exception: Exception) -> HttpResponseBase:
        if isinstance(exception, ApplicationError):
            return build_error_response(
                code=exception.code,
                message=exception.message,
                status=exception.status,
                details=exception.details,
            )

        if isinstance(exception, ValidationError):
            return build_error_response(
                code=ErrorCode.BAD_REQUEST,
                status=HTTPStatus.BAD_REQUEST,
                details=extract_validation_details(exception),
            )

        if isinstance(exception, Http404):
            return build_error_response(
                code=ErrorCode.NOT_FOUND,
                status=HTTPStatus.NOT_FOUND,
            )

        if isinstance(exception, PermissionDenied):
            return build_error_response(
                code=ErrorCode.FORBIDDEN,
                status=HTTPStatus.FORBIDDEN,
            )

        logger.exception("요청 수행 중 오류가 발생했습니다.")
        return build_internal_server_error_response()
