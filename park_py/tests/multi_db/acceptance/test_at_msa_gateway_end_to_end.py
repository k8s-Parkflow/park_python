from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from orchestration_service.application.errors import DownstreamError
from orchestration_service.models import SagaOperation
from parking_command_service.domains.parking_record.application.exceptions import (
    ParkingRecordBadRequestError,
    ParkingRecordConflictError,
    ParkingRecordNotFoundError,
)
from parking_command_service.domains.parking_record.domain import ParkingHistory, SlotOccupancy
from parking_command_service.grpc.application import ParkingCommandGrpcApplicationService
from parking_query_service.grpc.application import ParkingQueryGrpcApplicationService
from parking_query_service.models.current_parking_view import CurrentParkingView
from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType
from vehicle_service.services.lookup import VehicleLookupService
from zone_service.models import ParkingSlot as ZoneParkingSlot
from zone_service.models import SlotType, Zone
from zone_service.services.policy import ZonePolicyService


def _parse_iso(value: str | None):
    if value is None:
        return None
    return datetime.fromisoformat(value)


class DirectVehicleGateway:
    def __init__(self) -> None:
        self.lookup_service = VehicleLookupService()

    def get_vehicle(self, *, vehicle_num: str) -> dict:
        try:
            vehicle = self.lookup_service.get_vehicle(vehicle_num=vehicle_num)
        except Vehicle.DoesNotExist as error:
            raise DownstreamError(
                dependency="vehicle-service",
                error_code="not_found",
                message="vehicle not found",
                status=404,
            ) from error
        return {
            "vehicle_num": vehicle.vehicle_num,
            "vehicle_type": getattr(vehicle.vehicle_type, "value", vehicle.vehicle_type),
            "active": True,
        }


class DirectZoneGateway:
    def __init__(self) -> None:
        self.zone_policy_service = ZonePolicyService()

    def validate_entry_policy(self, *, slot_id: int, vehicle_type: str) -> dict:
        try:
            return self.zone_policy_service.validate_entry_policy(
                slot_id=slot_id,
                vehicle_type=vehicle_type,
            )
        except ZoneParkingSlot.DoesNotExist as error:
            raise DownstreamError(
                dependency="zone-service",
                error_code="not_found",
                message="parking slot not found",
                status=404,
            ) from error

    def get_zone(self, *, zone_id: int) -> dict:
        try:
            zone = self.zone_policy_service.get_zone(zone_id=zone_id)
        except Zone.DoesNotExist as error:
            raise DownstreamError(
                dependency="zone-service",
                error_code="not_found",
                message="zone not found",
                status=404,
            ) from error
        return {
            "zone_id": zone.zone_id,
            "zone_name": zone.zone_name,
            "is_active": zone.is_active,
        }


class DirectParkingCommandGateway:
    def __init__(self, *, vehicle_gateway: DirectVehicleGateway) -> None:
        self.application_service = ParkingCommandGrpcApplicationService(
            vehicle_repository=vehicle_gateway,
        )

    def create_entry(
        self,
        *,
        operation_id: str,
        vehicle_num: str,
        slot_id: int,
        zone_id: int,
        slot_code: str,
        slot_type: str,
        requested_at: str,
    ) -> dict:
        try:
            snapshot = self.application_service.create_entry(
                vehicle_num=vehicle_num,
                slot_id=slot_id,
                zone_id=zone_id,
                slot_code=slot_code,
                slot_type=slot_type,
                requested_at=_parse_iso(requested_at),
            )
        except (ParkingRecordNotFoundError, ParkingRecordBadRequestError, ParkingRecordConflictError) as error:
            raise _map_parking_command_error(error) from error
        return snapshot.to_dict()

    def compensate_entry(self, *, operation_id: str, history_id: int, slot_id: int, vehicle_num: str) -> dict:
        try:
            return self.application_service.compensate_entry(history_id=history_id)
        except ParkingRecordNotFoundError as error:
            raise _map_parking_command_error(error) from error

    def validate_active_parking(self, *, vehicle_num: str) -> dict:
        try:
            payload = self.application_service.validate_active_parking(vehicle_num=vehicle_num)
        except ParkingRecordNotFoundError as error:
            raise _map_parking_command_error(error) from error
        payload["entry_at"] = payload["entry_at"].isoformat()
        return payload

    def exit_parking(self, *, operation_id: str, vehicle_num: str, requested_at: str) -> dict:
        try:
            snapshot = self.application_service.exit_parking(
                vehicle_num=vehicle_num,
                requested_at=_parse_iso(requested_at),
            )
        except (ParkingRecordNotFoundError, ParkingRecordBadRequestError, ParkingRecordConflictError) as error:
            raise _map_parking_command_error(error) from error
        return snapshot.to_dict()

    def compensate_exit(self, *, operation_id: str, history_id: int, slot_id: int, vehicle_num: str) -> dict:
        try:
            return self.application_service.compensate_exit(history_id=history_id)
        except ParkingRecordNotFoundError as error:
            raise _map_parking_command_error(error) from error


class DirectParkingQueryGateway:
    def __init__(self) -> None:
        self.application_service = ParkingQueryGrpcApplicationService()

    def apply_entry_projection(self, **kwargs) -> dict:
        return self.application_service.apply_entry_projection(
            history_id=kwargs["history_id"],
            vehicle_num=kwargs["vehicle_num"],
            slot_id=kwargs["slot_id"],
            slot_code=kwargs["slot_code"],
            zone_id=kwargs["zone_id"],
            zone_name=kwargs["zone_name"],
            slot_type=kwargs["slot_type"],
            entry_at=_parse_iso(kwargs["entry_at"]),
        )

    def apply_exit_projection(self, **kwargs) -> dict:
        return self.application_service.apply_exit_projection(
            history_id=kwargs["history_id"],
            vehicle_num=kwargs["vehicle_num"],
        )

    def compensate_entry_projection(self, **kwargs) -> dict:
        return self.application_service.compensate_entry_projection(
            vehicle_num=kwargs["vehicle_num"],
        )

    def compensate_exit_projection(self, **kwargs) -> dict:
        return self.application_service.compensate_exit_projection(
            history_id=kwargs["history_id"],
            vehicle_num=kwargs["vehicle_num"],
            slot_id=kwargs["slot_id"],
            slot_code=kwargs["slot_code"],
            zone_id=kwargs["zone_id"],
            zone_name=kwargs["zone_name"],
            slot_type=kwargs["slot_type"],
            entry_at=_parse_iso(kwargs["entry_at"]),
        )


def _map_parking_command_error(error: Exception) -> DownstreamError:
    if isinstance(error, ParkingRecordNotFoundError):
        return DownstreamError(
            dependency="parking-command-service",
            error_code="not_found",
            message=str(error),
            status=404,
        )
    if isinstance(error, ParkingRecordBadRequestError):
        return DownstreamError(
            dependency="parking-command-service",
            error_code="invalid_argument",
            message=str(error),
            status=400,
        )
    return DownstreamError(
        dependency="parking-command-service",
        error_code="failed_precondition",
        message=str(error),
        status=409,
    )


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class MsaGatewayEndToEndAcceptanceTests(TestCase):
    databases = "__all__"

    def setUp(self) -> None:
        super().setUp()
        self.vehicle_gateway = DirectVehicleGateway()
        self.zone_gateway = DirectZoneGateway()
        self.parking_command_gateway = DirectParkingCommandGateway(
            vehicle_gateway=self.vehicle_gateway,
        )
        self.parking_query_gateway = DirectParkingQueryGateway()

    def _patch_gateways(self):
        return patch.multiple(
            "orchestration_service.dependencies",
            build_vehicle_gateway=lambda: self.vehicle_gateway,
            build_zone_gateway=lambda: self.zone_gateway,
            build_parking_command_gateway=lambda: self.parking_command_gateway,
            build_parking_query_gateway=lambda: self.parking_query_gateway,
        )

    def _seed_vehicle_and_slot(self) -> None:
        Vehicle.objects.using("vehicle").create(
            vehicle_num="12가3456",
            vehicle_type=VehicleType.General,
        )
        zone = Zone.objects.using("zone").create(zone_id=1, zone_name="A-1", is_active=True)
        slot_type = SlotType.objects.using("zone").create(slot_type_id=1, type_name="GENERAL")
        ZoneParkingSlot.objects.using("zone").create(
            slot_id=7,
            zone=zone,
            slot_type=slot_type,
            slot_code="A001",
            is_active=True,
        )

    def test_should_complete_entry_across_service_databases__when_gateway_runs_end_to_end(self) -> None:
        self._seed_vehicle_and_slot()
        call_command("sync_slot_lock_anchors")

        with self._patch_gateways():
            response = self.client.post(
                "/api/v1/parking/entries",
                data={
                    "vehicle_num": "12가3456",
                    "slot_id": 7,
                    "requested_at": "2026-03-10T10:00:00+09:00",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="msa-entry-001",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SagaOperation.objects.using("default").count(), 1)
        history = ParkingHistory.objects.using("parking_command").get(vehicle_num="12가3456")
        projection = CurrentParkingView.objects.using("parking_query").get(vehicle_num="12가3456")
        occupancy = SlotOccupancy.objects.using("parking_command").get(slot_id=7)

        self.assertEqual(history.slot_id, 7)
        self.assertEqual(history.zone_id, 1)
        self.assertEqual(history.slot_code, "A001")
        self.assertEqual(projection.slot_id, 7)
        self.assertEqual(projection.zone_name, "A-1")
        self.assertTrue(occupancy.occupied)

    def test_should_complete_exit_across_service_databases__when_gateway_runs_end_to_end(self) -> None:
        self._seed_vehicle_and_slot()
        call_command("sync_slot_lock_anchors")

        with self._patch_gateways():
            self.client.post(
                "/api/v1/parking/entries",
                data={
                    "vehicle_num": "12가3456",
                    "slot_id": 7,
                    "requested_at": "2026-03-10T10:00:00+09:00",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="msa-entry-002",
            )
            response = self.client.post(
                "/api/v1/parking/exits",
                data={
                    "vehicle_num": "12가3456",
                    "requested_at": "2026-03-10T12:00:00+09:00",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="msa-exit-001",
            )

        self.assertEqual(response.status_code, 200)
        history = ParkingHistory.objects.using("parking_command").get(vehicle_num="12가3456")
        occupancy = SlotOccupancy.objects.using("parking_command").get(slot_id=7)

        self.assertEqual(history.status, "EXITED")
        self.assertIsNotNone(history.exit_at)
        self.assertFalse(occupancy.occupied)
        self.assertFalse(
            CurrentParkingView.objects.using("parking_query").filter(vehicle_num="12가3456").exists()
        )
        self.assertEqual(SagaOperation.objects.using("default").count(), 2)

    def test_should_fail_entry_before_command_write__when_lock_anchor_sync_missing(self) -> None:
        self._seed_vehicle_and_slot()

        with self._patch_gateways():
            response = self.client.post(
                "/api/v1/parking/entries",
                data={
                    "vehicle_num": "12가3456",
                    "slot_id": 7,
                    "requested_at": "2026-03-10T10:00:00+09:00",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="msa-entry-003",
            )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(ParkingHistory.objects.using("parking_command").exists())
        self.assertFalse(
            CurrentParkingView.objects.using("parking_query").filter(vehicle_num="12가3456").exists()
        )
