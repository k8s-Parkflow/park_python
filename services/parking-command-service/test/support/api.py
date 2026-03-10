from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import patch

from django.test import Client
from django.http import HttpResponse

from parking_command_service.clients.grpc.parking_query import (
    ParkingQueryGrpcProjectionWriter,
)
from parking_command_service.clients.grpc.zone import ZoneGrpcClient
from parking_command_service.clients.grpc.vehicle import VehicleGrpcClient
from parking_command_service.domains.parking_record.application.services import (
    ParkingRecordCommandService,
)
from parking_command_service.domains.parking_record.infrastructure.repositories.parking_record_repository import (
    DjangoParkingRecordRepository,
)
from parking_query_service.grpc.servicers import ParkingQueryGrpcServicer
from park_py.tests.grpc_support import build_direct_stub
from vehicle_service.grpc.servicers import VehicleGrpcServicer
from zone_service.grpc.servicers import ZoneGrpcServicer


# 입차 API 호출 유틸리티
def post_entry(
    client: Client,
    *,
    vehicle_num: str,
    zone_id: int | None = None,
    slot_name: str | None = None,
    slot_id: int | None = None,
    entry_at: datetime | None = None,
) -> HttpResponse:
    payload: dict[str, object] = {"vehicle_num": vehicle_num}
    if zone_id is not None:
        payload["zone_id"] = zone_id
    if slot_name is not None:
        payload["slot_name"] = slot_name
    if slot_id is not None:
        payload["slot_id"] = slot_id
    if entry_at is not None:
        payload["entry_at"] = entry_at.isoformat()
    with patch(
        "parking_command_service.domains.parking_record.presentation.http.views.get_parking_record_command_service",
        return_value=build_test_command_service(),
    ):
        return client.post(
            "/api/parking/entry",
            data=json.dumps(payload),
            content_type="application/json",
        )


# 출차 API 호출 유틸리티
def post_exit(
    client: Client,
    *,
    vehicle_num: str,
    zone_id: int | None = None,
    slot_name: str | None = None,
    slot_id: int | None = None,
    exit_at: datetime | None = None,
) -> HttpResponse:
    payload: dict[str, object] = {"vehicle_num": vehicle_num}
    if zone_id is not None:
        payload["zone_id"] = zone_id
    if slot_name is not None:
        payload["slot_name"] = slot_name
    if slot_id is not None:
        payload["slot_id"] = slot_id
    if exit_at is not None:
        payload["exit_at"] = exit_at.isoformat()
    with patch(
        "parking_command_service.domains.parking_record.presentation.http.views.get_parking_record_command_service",
        return_value=build_test_command_service(),
    ):
        return client.post(
            "/api/parking/exit",
            data=json.dumps(payload),
            content_type="application/json",
        )


def build_test_command_service() -> ParkingRecordCommandService:
    return ParkingRecordCommandService(
        parking_record_repository=DjangoParkingRecordRepository(),
        vehicle_repository=VehicleGrpcClient(
            stub=build_direct_stub(
                servicer=VehicleGrpcServicer(),
                method_names=["GetVehicle"],
            )
        ),
        zone_policy_gateway=ZoneGrpcClient(
            stub=build_direct_stub(
                servicer=ZoneGrpcServicer(),
                method_names=["ValidateEntryPolicy"],
            )
        ),
        projection_writer=build_test_projection_writer(),
    )


def build_test_projection_writer() -> ParkingQueryGrpcProjectionWriter:
    return ParkingQueryGrpcProjectionWriter(
        stub=build_direct_stub(
            servicer=ParkingQueryGrpcServicer(),
            method_names=["ApplyEntryProjection", "ApplyExitProjection"],
        ),
        zone_lookup=ZoneGrpcClient(
            stub=build_direct_stub(
                servicer=ZoneGrpcServicer(),
                method_names=["GetZone"],
            )
        ),
    )
