from unittest.mock import patch

from django.test import TestCase, override_settings

from parking_query_service.models import CurrentParkingView, ZoneAvailability


@override_settings(ROOT_URLCONF="park_py.urls")
class InternalProjectionViewContractTests(TestCase):
    def test_should_return_current_parking__when_projection_exists(self) -> None:
        with patch(
            "parking_query_service.views.get_current_parking",
            return_value={
                "vehicle_num": "69가-3455",
                "slot_id": 11,
                "zone_id": 1,
                "slot_type": "GENERAL",
                "entry_at": "2026-03-12T09:00:00+09:00",
            },
        ):
            response = self.client.get("/internal/parking-query/current-parking/69가-3455")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "vehicle_num": "69가-3455",
                "slot_id": 11,
                "zone_id": 1,
                "slot_type": "GENERAL",
                "entry_at": "2026-03-12T09:00:00+09:00",
            },
        )

    def test_should_return_not_found__when_current_parking_missing(self) -> None:
        with patch(
            "parking_query_service.views.get_current_parking",
            side_effect=CurrentParkingView.DoesNotExist(),
        ):
            response = self.client.get("/internal/parking-query/current-parking/69가-3455")

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

    def test_should_project_entry__when_payload_valid(self) -> None:
        with patch(
            "parking_query_service.views.project_entry",
            return_value={"projected": True},
        ):
            response = self.client.post(
                "/internal/parking-query/entries",
                data={
                    "operation_id": "op-001",
                    "vehicle_num": "69가-3455",
                    "slot_id": 11,
                    "zone_id": 1,
                    "slot_type": "GENERAL",
                    "entry_at": "2026-03-12T09:00:00+09:00",
                },
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"projected": True})

    def test_should_return_not_found__when_project_entry_zone_missing(self) -> None:
        with patch(
            "parking_query_service.views.project_entry",
            side_effect=ZoneAvailability.DoesNotExist(),
        ):
            response = self.client.post(
                "/internal/parking-query/entries",
                data={
                    "operation_id": "op-001",
                    "vehicle_num": "69가-3455",
                    "slot_id": 11,
                    "zone_id": 1,
                    "slot_type": "GENERAL",
                    "entry_at": "2026-03-12T09:00:00+09:00",
                },
                content_type="application/json",
            )

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

    def test_should_revert_entry__when_payload_valid(self) -> None:
        with patch(
            "parking_query_service.views.revert_entry",
            return_value={"reverted": True},
        ):
            response = self.client.post(
                "/internal/parking-query/entries/compensations",
                data={
                    "operation_id": "op-001",
                    "vehicle_num": "69가-3455",
                },
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"reverted": True})

    def test_should_project_exit__when_payload_valid(self) -> None:
        with patch(
            "parking_query_service.views.project_exit",
            return_value={"projected": True},
        ):
            response = self.client.post(
                "/internal/parking-query/exits",
                data={
                    "operation_id": "op-001",
                    "vehicle_num": "69가-3455",
                },
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"projected": True})

    def test_should_return_not_found__when_project_exit_projection_missing(self) -> None:
        with patch(
            "parking_query_service.views.project_exit",
            side_effect=CurrentParkingView.DoesNotExist(),
        ):
            response = self.client.post(
                "/internal/parking-query/exits",
                data={
                    "operation_id": "op-001",
                    "vehicle_num": "69가-3455",
                },
                content_type="application/json",
            )

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

    def test_should_restore_exit__when_payload_valid(self) -> None:
        with patch(
            "parking_query_service.views.restore_exit",
            return_value={"restored": True},
        ):
            response = self.client.post(
                "/internal/parking-query/exits/compensations",
                data={
                    "operation_id": "op-001",
                    "vehicle_num": "69가-3455",
                    "slot_id": 11,
                    "zone_id": 1,
                    "slot_type": "GENERAL",
                    "entry_at": "2026-03-12T09:00:00+09:00",
                },
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"restored": True})

    def test_should_return_not_found__when_restore_exit_zone_missing(self) -> None:
        with patch(
            "parking_query_service.views.restore_exit",
            side_effect=ZoneAvailability.DoesNotExist(),
        ):
            response = self.client.post(
                "/internal/parking-query/exits/compensations",
                data={
                    "operation_id": "op-001",
                    "vehicle_num": "69가-3455",
                    "slot_id": 11,
                    "zone_id": 1,
                    "slot_type": "GENERAL",
                    "entry_at": "2026-03-12T09:00:00+09:00",
                },
                content_type="application/json",
            )

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
