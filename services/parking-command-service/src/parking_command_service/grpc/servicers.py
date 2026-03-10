from __future__ import annotations

import grpc

from contracts.gen.python.parking_command.v1 import parking_command_pb2_grpc
from parking_command_service.domains.parking_record.application.exceptions import (
    ParkingRecordBadRequestError,
    ParkingRecordConflictError,
    ParkingRecordNotFoundError,
)
from parking_command_service.grpc.application import ParkingCommandGrpcApplicationService
from parking_command_service.grpc.mappers import (
    build_compensate_entry_response,
    build_compensate_exit_response,
    build_create_entry_response,
    build_exit_parking_response,
    build_validate_active_parking_response,
    timestamp_to_datetime,
)


class ParkingCommandGrpcServicer(parking_command_pb2_grpc.ParkingCommandServiceServicer):
    def __init__(
        self,
        *,
        application_service: ParkingCommandGrpcApplicationService | None = None,
    ) -> None:
        self.application_service = application_service or ParkingCommandGrpcApplicationService()

    def CreateEntry(self, request, context):  # noqa: N802
        try:
            snapshot = self.application_service.create_entry(
                vehicle_num=request.vehicle_num,
                slot_id=request.slot_id,
                requested_at=timestamp_to_datetime(request.context.requested_at),
            )
        except (ParkingRecordNotFoundError, ParkingRecordBadRequestError, ParkingRecordConflictError) as error:
            _abort_for_record_error(context=context, error=error)

        return build_create_entry_response(snapshot=snapshot)

    def CompensateEntry(self, request, context):  # noqa: N802
        try:
            payload = self.application_service.compensate_entry(history_id=request.history_id)
        except ParkingRecordNotFoundError as error:
            _abort_for_record_error(context=context, error=error)

        return build_compensate_entry_response(payload=payload)

    def ValidateActiveParking(self, request, context):  # noqa: N802
        try:
            payload = self.application_service.validate_active_parking(
                vehicle_num=request.vehicle_num
            )
        except ParkingRecordNotFoundError as error:
            _abort_for_record_error(context=context, error=error)

        return build_validate_active_parking_response(payload=payload)

    def ExitParking(self, request, context):  # noqa: N802
        try:
            snapshot = self.application_service.exit_parking(
                vehicle_num=request.vehicle_num,
                requested_at=timestamp_to_datetime(request.context.requested_at),
            )
        except (ParkingRecordNotFoundError, ParkingRecordBadRequestError, ParkingRecordConflictError) as error:
            _abort_for_record_error(context=context, error=error)

        return build_exit_parking_response(snapshot=snapshot)

    def CompensateExit(self, request, context):  # noqa: N802
        try:
            payload = self.application_service.compensate_exit(history_id=request.history_id)
        except ParkingRecordNotFoundError as error:
            _abort_for_record_error(context=context, error=error)

        return build_compensate_exit_response(payload=payload)


def _abort_for_record_error(*, context, error) -> None:
    if isinstance(error, ParkingRecordNotFoundError):
        context.abort(grpc.StatusCode.NOT_FOUND, str(error))
    if isinstance(error, ParkingRecordBadRequestError):
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))
    context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(error))
