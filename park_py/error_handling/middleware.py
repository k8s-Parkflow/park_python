import logging
from http import HTTPStatus

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpRequest
from django.http.response import HttpResponseBase

from park_py.error_handling.error_codes import ErrorCode
from park_py.error_handling.exceptions import ApplicationError
from park_py.error_handling.responses import (
    build_error_response,
    build_internal_server_error_response,
    extract_validation_details,
)

logger = logging.getLogger(__name__)


class ExceptionHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        try:
            return self.get_response(request)

        except ApplicationError as exception:
            return build_error_response(
                code=exception.code,
                message=exception.message,
                status=exception.status,
                details=exception.details,
            )

        except ValidationError as exception:
            return build_error_response(
                code=ErrorCode.BAD_REQUEST,
                status=HTTPStatus.BAD_REQUEST,
                details=extract_validation_details(exception),
            )

        except Http404:
            return build_error_response(
                code=ErrorCode.NOT_FOUND,
                status=HTTPStatus.NOT_FOUND,
            )

        except PermissionDenied:
            return build_error_response(
                code=ErrorCode.FORBIDDEN,
                status=HTTPStatus.FORBIDDEN,
            )

        except Exception:
            logger.exception("🚨요청수행 중 에러 발생")
            return build_internal_server_error_response()
