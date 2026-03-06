from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

from park_py.error_handling.error_codes import ErrorCode, resolve_error_message


class ApplicationError(Exception):
    def __init__(
        self,
        message: str = "",
        *,
        code: Union[ErrorCode, str] = ErrorCode.APPLICATION_ERROR,
        status: int = HTTPStatus.BAD_REQUEST,
        details: Optional[Union[Dict[str, Any], List[Any]]] = None,
    ) -> None:
        resolved_message = resolve_error_message(code, message)
        super().__init__(resolved_message)
        self.message = resolved_message
        self.code = code
        self.status = status
        self.details = details
