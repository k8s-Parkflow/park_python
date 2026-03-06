from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from park_py.error_handling.error_codes import (
    ErrorCode,
    resolve_error_message,
    serialize_error_code,
)


def build_error_response(
    *,
    code: Union[ErrorCode, str],
    message: str = "",
    status: int,
    details: Optional[Union[Dict[str, Any], List[Any]]] = None,
) -> JsonResponse:
    payload: Dict[str, Any] = {
        "error": {
            "code": serialize_error_code(code),
            "message": resolve_error_message(code, message),
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return JsonResponse(payload, status=status)


def extract_validation_details(exception: ValidationError) -> Union[Dict[str, Any], List[Any]]:
    if hasattr(exception, "message_dict"):
        return exception.message_dict
    return exception.messages


def build_internal_server_error_response() -> JsonResponse:
    details: Optional[Dict[str, Any]] = None
    if settings.DEBUG:
        details = {"message": "자세한 내용은 서버 로그를 확인하세요."}

    return build_error_response(
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        details=details,
    )
