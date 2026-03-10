from __future__ import annotations

import os

import grpc

from contracts.gen.python.parking_query.v1 import parking_query_pb2, parking_query_pb2_grpc
from parking_command_service.clients.grpc.base import (
    DownstreamDependencyError,
    GrpcClientBase,
    build_request_context,
)
from parking_command_service.clients.grpc.zone import ZoneGrpcClient


class ParkingQueryGrpcProjectionWriter(GrpcClientBase):
    def __init__(
        self,
        *,
        target: str | None = None,
        timeout: float = 5.0,
        channel: grpc.Channel | None = None,
        stub=None,
        zone_lookup=None,
    ) -> None:
        super().__init__(
            target=target or os.getenv("PARKING_QUERY_SERVICE_GRPC_TARGET", "127.0.0.1:50054"),
            timeout=timeout,
            channel=channel,
            stub=stub,
        )
        self.zone_lookup = zone_lookup or ZoneGrpcClient()

    def record_entry(self, *, history) -> None:
        zone_payload = self.zone_lookup.get_zone(zone_id=_history_zone_id(history))
        request = parking_query_pb2.ApplyEntryProjectionRequest(
            context=build_request_context(requested_at=history.entry_at.isoformat()),
            operation_id=f"http-entry-{history.history_id}",
            history_id=history.history_id,
            vehicle_num=history.vehicle_num,
            slot_id=history.slot_id,
            zone_id=_history_zone_id(history),
            zone_name=zone_payload["zone_name"],
            slot_type=_slot_type_name(slot_type_id=_history_slot_type_id(history)),
            slot_code=_history_slot_code(history),
        )
        request.entry_at.CopyFrom(request.context.requested_at)
        self._invoke(stub_method_name="ApplyEntryProjection", request=request)

    def record_exit(self, *, history) -> None:
        exit_at = history.exit_at or history.entry_at
        request = parking_query_pb2.ApplyExitProjectionRequest(
            context=build_request_context(requested_at=exit_at.isoformat()),
            operation_id=f"http-exit-{history.history_id}",
            history_id=history.history_id,
            vehicle_num=history.vehicle_num,
            slot_id=history.slot_id,
            zone_id=_history_zone_id(history),
            slot_type=_slot_type_name(slot_type_id=_history_slot_type_id(history)),
            slot_code=_history_slot_code(history),
        )
        request.exit_at.CopyFrom(request.context.requested_at)
        self._invoke(stub_method_name="ApplyExitProjection", request=request)

    def _invoke(self, *, stub_method_name: str, request) -> None:
        stub = self.get_stub(parking_query_pb2_grpc.ParkingQueryServiceStub)
        rpc_call = getattr(stub, stub_method_name)
        try:
            rpc_call(request, timeout=self.timeout)
        except grpc.RpcError as error:
            raise DownstreamDependencyError(
                message="주차 조회 프로젝션 서비스 호출에 실패했습니다."
            ) from error


def _slot_type_name(*, slot_type_id: int) -> str:
    return {
        1: "GENERAL",
        2: "EV",
        3: "DISABLED",
    }.get(slot_type_id, str(slot_type_id))


def _history_zone_id(history) -> int:
    zone_id = getattr(history, "zone_id", 0) or 0
    if zone_id:
        return zone_id
    return history.slot.zone_id


def _history_slot_type_id(history) -> int:
    slot_type_id = getattr(history, "slot_type_id", 0) or 0
    if slot_type_id:
        return slot_type_id
    return history.slot.slot_type_id


def _history_slot_code(history) -> str:
    slot_code = getattr(history, "slot_code", "")
    if slot_code:
        return slot_code
    return history.slot.slot_code
