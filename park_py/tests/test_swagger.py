from django.test import SimpleTestCase, override_settings


@override_settings(ROOT_URLCONF="park_py.urls")
class SwaggerDocsTests(SimpleTestCase):
    def test_openapi_json_returns_gateway_paths(self) -> None:
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["openapi"], "3.0.3")
        self.assertIn("/api/v1/parking/entries", payload["paths"])
        self.assertEqual(payload["servers"], [{"url": "/"}])

    def test_swagger_ui_returns_html_document(self) -> None:
        response = self.client.get("/swagger/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SwaggerUIBundle")
        self.assertContains(response, 'url: "/openapi.json"')
        self.assertNotContains(response, 'url: "http://')
        self.assertNotContains(response, 'url: "https://')
