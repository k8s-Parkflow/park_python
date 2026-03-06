from django.test import SimpleTestCase, override_settings


@override_settings(ROOT_URLCONF="park_py.urls_test")
class ExceptionHandlingMiddlewareTests(SimpleTestCase):
    def test_application_error_returns_consistent_payload(self) -> None:
        response = self.client.get("/test-errors/application/")

        self.assertEqual(response.status_code, 409)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "conflict",
                    "message": "요청한 리소스의 상태가 현재 요청과 충돌합니다.",
                    "details": {"reason": "이미 처리된 요청입니다."},
                }
            },
        )

    def test_validation_error_returns_bad_request_payload(self) -> None:
        response = self.client.get("/test-errors/validation/")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"field": ["필수 입력값입니다."]},
                }
            },
        )

    def test_permission_denied_returns_forbidden_payload(self) -> None:
        response = self.client.get("/test-errors/permission/")

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "forbidden",
                    "message": "이 작업을 수행할 권한이 없습니다.",
                }
            },
        )

    @override_settings(DEBUG=True)
    def test_unknown_error_returns_internal_server_error_payload(self) -> None:
        with self.assertLogs("park_py.error_handling.middleware", level="ERROR"):
                response = self.client.get("/test-errors/runtime/")

        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "서버 내부 오류가 발생했습니다.",
                    "details": {"message": "자세한 내용은 서버 로그를 확인하세요."},
                }
            },
        )

    def test_not_found_returns_consistent_payload(self) -> None:
        response = self.client.get("/test-errors/missing/")

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "not_found",
                    "message": "요청한 리소스를 찾을 수 없습니다.",
                }
            },
        )
