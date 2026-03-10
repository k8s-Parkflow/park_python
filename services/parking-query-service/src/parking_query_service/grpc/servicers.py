from __future__ import annotations

import grpc

from contracts.gen.python.parking_query.v1 import parking_query_pb2_grpc
from parking_query_service.grpc.application import (
    ParkingQueryGrpcApplicationService,
    ParkingQueryProjectionNotFoundError,
)
from parking_query_service.grpc.mappers import (
    build_apply_entry_response,
    build_apply_exit_response,
    build_compensate_entry_response,
    build_compensate_exit_response,
    build_current_parking_response,
    build_zone_availability_response,
    timestamp_to_datetime,
)


class ParkingQueryGrpcServicer(parking_query_pb2_grpc.ParkingQueryServiceServicer):
    def __init__(
        self,
        *,
        application_service: ParkingQueryGrpcApplicationService | None = None,
    ) -> None:
        self.application_service = application_service or ParkingQueryGrpcApplicationService()

    def ApplyEntryProjection(self, request, context):  # noqa: N802, ARG002
        payload = self.application_service.apply_entry_projection(
            history_id=request.history_id,
            vehicle_num=request.vehicle_num,
            slot_id=request.slot_id,
            zone_id=request.zone_id,
            slot_type=request.slot_type,
            entry_at=timestamp_to_datetime(request.entry_at),
        )
        return build_apply_entry_response(payload=payload)

    def ApplyExitProjection(self, request, context):  # noqa: N802, ARG002
        payload = self.application_service.apply_exit_projection(vehicle_num=request.vehicle_num)
        return build_apply_exit_response(payload=payload)

    def CompensateEntryProjection(self, request, context):  # noqa: N802, ARG002
        payload = self.application_service.compensate_entry_projection(
            vehicle_num=request.vehicle_num
        )
        return build_compensate_entry_response(payload=payload)

    def CompensateExitProjection(self, request, context):  # noqa: N802, ARG002
        payload = self.application_service.compensate_exit_projection(
            history_id=request.history_id,
            vehicle_num=request.vehicle_num,
            slot_id=request.slot_id,
            zone_id=request.zone_id,
            slot_type=request.slot_type,
            entry_at=timestamp_to_datetime(request.entry_at),
        )
        return build_compensate_exit_response(payload=payload)

    def GetCurrentParking(self, request, context):  # noqa: N802
        try:
            payload = self.application_service.get_current_parking(vehicle_num=request.vehicle_num)
        except ParkingQueryProjectionNotFoundError as error:
            context.abort(grpc.StatusCode.NOT_FOUND, str(error))
        return build_current_parking_response(payload=payload)

    def GetZoneAvailability(self, request, context):  # noqa: N802, ARG002
        payload = self.application_service.get_zone_availability(slot_type=request.slot_type)
        return build_zone_availability_response(payload=payload)
