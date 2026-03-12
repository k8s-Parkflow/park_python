from shared.error_handling import ErrorCode
from shared.error_handling.error_codes import serialize_error_code


class GatewayErrorMapper:
    def map(self, *, dependency: str, status_code: int, error_code: str) -> dict:
        if status_code == 409:
            code = ErrorCode.CONFLICT
        else:
            code = ErrorCode.APPLICATION_ERROR

        return {
            "status": status_code,
            "code": serialize_error_code(code),
            "details": {
                "dependency": dependency,
                "error_code": error_code,
            },
        }
