from enum import Enum
from typing import Union


class ErrorCode(Enum):
    APPLICATION_ERROR = ("application_error", "요청을 처리하는 중 오류가 발생했습니다.")
    BAD_REQUEST = ("bad_request", "잘못된 요청입니다.")
    CONFLICT = ("conflict", "요청한 리소스의 상태가 현재 요청과 충돌합니다.")
    FORBIDDEN = ("forbidden", "이 작업을 수행할 권한이 없습니다.")
    INTERNAL_SERVER_ERROR = ("internal_server_error", "서버 내부 오류가 발생했습니다.")
    NOT_FOUND = ("not_found", "요청한 리소스를 찾을 수 없습니다.")

    @property
    def code(self) -> str:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]


def serialize_error_code(code: Union[str, Enum]) -> str:
    if isinstance(code, ErrorCode):
        return code.code
    if isinstance(code, Enum):
        return str(code.value)
    return code


def resolve_error_message(code: Union[str, Enum], message: str = "") -> str:
    if message:
        return message
    if isinstance(code, ErrorCode):
        return code.message
    return "오류가 발생했습니다."
