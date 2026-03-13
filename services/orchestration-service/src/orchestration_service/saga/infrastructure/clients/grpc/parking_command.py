from __future__ import annotations

import os

import grpc

from contracts.gen.python.parking_command.v1 import (
    parking_command_pb2,
    parking_command_pb2_grpc,
)
from orchestration_service.saga.infrastructure.clients.grpc.base import (
    GrpcClientBase,
    build_request_context,
)


def _timestamp_to_iso_or_none(timestamp) -> str | None:
    if timestamp.seconds == 0 and timestamp.nanos == 0:
        return None
    return timestamp.ToDatetime().isoformat()


def _build_entry_payload(response) -> dict:
    return {
        "history_id": response.history_id,
        "slot_id": response.slot_id,
        "vehicle_num": response.vehicle_num,
        "entry_at": _timestamp_to_iso_or_none(response.entry_at),
        "status": response.status,
        "slot_code": response.slot_code,
    }


def _build_compensation_payload(response) -> dict:
    return {
        "history_id": response.history_id,
        "slot_released": response.slot_released,
        "compensated_at": _timestamp_to_iso_or_none(response.compensated_at),
    }


def _build_active_parking_payload(response) -> dict:
    return {
        "history_id": response.history_id,
        "slot_id": response.slot_id,
        "vehicle_num": response.vehicle_num,
        "entry_at": _timestamp_to_iso_or_none(response.entry_at),
        "status": response.status,
        "zone_id": response.zone_id,
        "slot_type": response.slot_type,
        "slot_code": response.slot_code,
    }


def _build_exit_payload(response) -> dict:
    return {
        "history_id": response.history_id,
        "slot_id": response.slot_id,
        "vehicle_num": response.vehicle_num,
        "exit_at": _timestamp_to_iso_or_none(response.exit_at),
        "status": response.status,
        "slot_code": response.slot_code,
    }


def _build_exit_compensation_payload(response) -> dict:
    return {
        "history_id": response.history_id,
        "slot_occupied": response.slot_occupied,
        "compensated_at": _timestamp_to_iso_or_none(response.compensated_at),
    }


def _build_create_entry_request(
    *,
    operation_id: str,
    vehicle_num: str,
    slot_id: int,
    zone_id: int,
    slot_code: str,
    slot_type: str,
    requested_at: str,
):
    return parking_command_pb2.CreateEntryRequest(
        context=build_request_context(requested_at=requested_at),
        operation_id=operation_id,
        vehicle_num=vehicle_num,
        slot_id=slot_id,
        zone_id=zone_id,
        slot_code=slot_code,
        slot_type=slot_type,
    )


class ParkingCommandGrpcClient(GrpcClientBase):
    def __init__(
        self,
        *,
        target: str | None = None,
        timeout: float = 5.0,
        channel: grpc.Channel | None = None,
        stub=None,
    ) -> None:
        super().__init__(
            target=target or os.getenv("PARKING_COMMAND_SERVICE_GRPC_TARGET", "127.0.0.1:50017"),
            timeout=timeout,
            channel=channel,
            stub=stub,
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
        stub = self.get_stub(parking_command_pb2_grpc.ParkingCommandServiceStub)
        request = _build_create_entry_request(
            operation_id=operation_id,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
            zone_id=zone_id,
            slot_code=slot_code,
            slot_type=slot_type,
            requested_at=requested_at,
        )
        response = self.invoke_unary(
            dependency="parking-command-service",
            rpc_call=stub.CreateEntry,
            request=request,
        )
        return _build_entry_payload(response)

    def compensate_entry(
        self,
        *,
        operation_id: str,
        history_id: int,
        slot_id: int,
        vehicle_num: str,
    ) -> dict:
        stub = self.get_stub(parking_command_pb2_grpc.ParkingCommandServiceStub)
        request = parking_command_pb2.CompensateEntryRequest(
            context=build_request_context(),
            operation_id=operation_id,
            history_id=history_id,
            slot_id=slot_id,
            vehicle_num=vehicle_num,
        )
        response = self.invoke_unary(
            dependency="parking-command-service",
            rpc_call=stub.CompensateEntry,
            request=request,
        )
        return _build_compensation_payload(response)

    def validate_active_parking(self, *, vehicle_num: str) -> dict:
        stub = self.get_stub(parking_command_pb2_grpc.ParkingCommandServiceStub)
        request = parking_command_pb2.ValidateActiveParkingRequest(
            context=build_request_context(),
            vehicle_num=vehicle_num,
        )
        response = self.invoke_unary(
            dependency="parking-command-service",
            rpc_call=stub.ValidateActiveParking,
            request=request,
        )
        return _build_active_parking_payload(response)

    def exit_parking(
        self,
        *,
        operation_id: str,
        vehicle_num: str,
        requested_at: str,
    ) -> dict:
        stub = self.get_stub(parking_command_pb2_grpc.ParkingCommandServiceStub)
        request = parking_command_pb2.ExitParkingRequest(
            context=build_request_context(requested_at=requested_at),
            operation_id=operation_id,
            vehicle_num=vehicle_num,
        )
        response = self.invoke_unary(
            dependency="parking-command-service",
            rpc_call=stub.ExitParking,
            request=request,
        )
        return _build_exit_payload(response)

    def compensate_exit(
        self,
        *,
        operation_id: str,
        history_id: int,
        slot_id: int,
        vehicle_num: str,
    ) -> dict:
        stub = self.get_stub(parking_command_pb2_grpc.ParkingCommandServiceStub)
        request = parking_command_pb2.CompensateExitRequest(
            context=build_request_context(),
            operation_id=operation_id,
            history_id=history_id,
            slot_id=slot_id,
            vehicle_num=vehicle_num,
        )
        response = self.invoke_unary(
            dependency="parking-command-service",
            rpc_call=stub.CompensateExit,
            request=request,
        )
        return _build_exit_compensation_payload(response)


__all__ = ["ParkingCommandGrpcClient"]
