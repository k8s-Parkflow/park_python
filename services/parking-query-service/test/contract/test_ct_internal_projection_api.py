from django.test import TestCase, override_settings


@override_settings(ROOT_URLCONF="park_py.urls")
class InternalProjectionApiContractTests(TestCase):
    def test_should_return_bad_request__when_projection_body_is_malformed_json(self) -> None:
        response = self.client.post(
            "/internal/parking-query/entries",
            data='{"operation_id":"op-001"',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"body": ["JSON 본문 형식이 올바르지 않습니다."]},
                }
            },
        )

    def test_should_return_bad_request__when_projection_body_is_not_object(self) -> None:
        response = self.client.post(
            "/internal/parking-query/entries",
            data='["op-001"]',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"body": ["JSON 객체만 허용됩니다."]},
                }
            },
        )

    def test_should_return_bad_request__when_projection_required_field_is_missing(self) -> None:
        response = self.client.post(
            "/internal/parking-query/exits",
            data={"operation_id": "op-001"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"vehicle_num": ["필수 입력값입니다."]},
                }
            },
        )
