from django.test import SimpleTestCase, override_settings


# Swagger UI CSRF 쿠키 주입 테스트 클래스
@override_settings(ROOT_URLCONF="park_py.urls_openapi_test")
class SwaggerUiViewTests(SimpleTestCase):
    # Swagger 로드 시 CSRF 쿠키 설정 검증
    def test_should_set_csrf_cookie__when_swagger_loaded(self) -> None:
        # Given / When
        response = self.client.get("/api/docs/swagger")

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)

    # Swagger 로드 시 CSRF 헤더 주입 스크립트 검증
    def test_should_embed_csrf_interceptor__when_swagger_loaded(self) -> None:
        # Given / When
        response = self.client.get("/api/docs/swagger")

        # Then
        content = response.content.decode()
        self.assertIn("requestInterceptor", content)
        self.assertIn("X-CSRFToken", content)
        self.assertIn('request.credentials = "same-origin";', content)
