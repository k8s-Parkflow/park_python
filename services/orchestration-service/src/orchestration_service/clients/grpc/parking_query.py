from __future__ import annotations

import os

import grpc

from contracts.gen.python.parking_query.v1 import parking_query_pb2, parking_query_pb2_grpc
from orchestration_service.clients.grpc.base import GrpcClientBase, build_request_context


def _timestamp_to_iso_or_none(timestamp) -> str | None:
    if timestamp.seconds == 0 and timestamp.nanos == 0:
        return None
    return timestamp.ToDatetime().isoformat()


def _build_projection_result(*, projected: bool, updated_at) -> dict:
    return {
        "projected": projected,
        "updated_at": _timestamp_to_iso_or_none(updated_at),
    }


def _build_compensation_result(*, compensated: bool, updated_at) -> dict:
    return {
        "compensated": compensated,
        "updated_at": _timestamp_to_iso_or_none(updated_at),
    }


class ParkingQueryGrpcClient(GrpcClientBase):
    def __init__(
        self,
        *,
        target: str | None = None,
        timeout: float = 5.0,
        channel: grpc.Channel | None = None,
        stub=None,
    ) -> None:
        super().__init__(
            target=target or os.getenv("PARKING_QUERY_SERVICE_GRPC_TARGET", "127.0.0.1:50054"),
            timeout=timeout,
            channel=channel,
            stub=stub,
        )

    def apply_entry_projection(
        self,
        *,
        operation_id: str,
        history_id: int,
        vehicle_num: str,
        slot_id: int,
        slot_code: str,
        zone_id: int,
        zone_name: str,
        slot_type: str,
        entry_at: str,
    ) -> dict:
        stub = self.get_stub(parking_query_pb2_grpc.ParkingQueryServiceStub)
        request = parking_query_pb2.ApplyEntryProjectionRequest(
            context=build_request_context(requested_at=entry_at),
            operation_id=operation_id,
            history_id=history_id,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
            zone_id=zone_id,
            slot_type=slot_type,
            slot_code=slot_code,
            zone_name=zone_name,
        )
        request.entry_at.CopyFrom(request.context.requested_at)
        response = self.invoke_unary(
            dependency="parking-query-service",
            rpc_call=stub.ApplyEntryProjection,
            request=request,
        )
        return _build_projection_result(
            projected=response.projected,
            updated_at=response.updated_at,
        )

    def apply_exit_projection(
        self,
        *,
        operation_id: str,
        history_id: int,
        vehicle_num: str,
        slot_id: int,
        slot_code: str,
        zone_id: int,
        slot_type: str,
        exit_at: str,
    ) -> dict:
        stub = self.get_stub(parking_query_pb2_grpc.ParkingQueryServiceStub)
        request = parking_query_pb2.ApplyExitProjectionRequest(
            context=build_request_context(requested_at=exit_at),
            operation_id=operation_id,
            history_id=history_id,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
            zone_id=zone_id,
            slot_type=slot_type,
            slot_code=slot_code,
        )
        request.exit_at.CopyFrom(request.context.requested_at)
        response = self.invoke_unary(
            dependency="parking-query-service",
            rpc_call=stub.ApplyExitProjection,
            request=request,
        )
        return _build_projection_result(
            projected=response.projected,
            updated_at=response.updated_at,
        )

    def compensate_entry_projection(
        self,
        *,
        operation_id: str,
        history_id: int,
        vehicle_num: str,
        zone_id: int,
        slot_type: str,
    ) -> dict:
        stub = self.get_stub(parking_query_pb2_grpc.ParkingQueryServiceStub)
        request = parking_query_pb2.CompensateEntryProjectionRequest(
            context=build_request_context(),
            operation_id=operation_id,
            history_id=history_id,
            vehicle_num=vehicle_num,
            zone_id=zone_id,
            slot_type=slot_type,
        )
        response = self.invoke_unary(
            dependency="parking-query-service",
            rpc_call=stub.CompensateEntryProjection,
            request=request,
        )
        return _build_compensation_result(
            compensated=response.compensated,
            updated_at=response.updated_at,
        )

    def compensate_exit_projection(
        self,
        *,
        operation_id: str,
        history_id: int,
        vehicle_num: str,
        slot_id: int,
        slot_code: str,
        zone_id: int,
        zone_name: str,
        slot_type: str,
        entry_at: str,
    ) -> dict:
        stub = self.get_stub(parking_query_pb2_grpc.ParkingQueryServiceStub)
        request = parking_query_pb2.CompensateExitProjectionRequest(
            context=build_request_context(requested_at=entry_at),
            operation_id=operation_id,
            history_id=history_id,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
            zone_id=zone_id,
            slot_type=slot_type,
            slot_code=slot_code,
            zone_name=zone_name,
        )
        request.entry_at.CopyFrom(request.context.requested_at)
        response = self.invoke_unary(
            dependency="parking-query-service",
            rpc_call=stub.CompensateExitProjection,
            request=request,
        )
        return _build_compensation_result(
            compensated=response.compensated,
            updated_at=response.updated_at,
        )

    def get_current_parking(self, *, vehicle_num: str) -> dict:
        stub = self.get_stub(parking_query_pb2_grpc.ParkingQueryServiceStub)
        request = parking_query_pb2.GetCurrentParkingRequest(vehicle_num=vehicle_num)
        response = self.invoke_unary(
            dependency="parking-query-service",
            rpc_call=stub.GetCurrentParking,
            request=request,
        )
        return {
            "vehicle_num": response.vehicle_num,
            "slot_id": response.slot_id,
            "zone_id": response.zone_id,
            "slot_type": response.slot_type,
            "entry_at": _timestamp_to_iso_or_none(response.entry_at),
            "updated_at": _timestamp_to_iso_or_none(response.updated_at),
            "slot_code": response.slot_code,
            "zone_name": response.zone_name,
        }
