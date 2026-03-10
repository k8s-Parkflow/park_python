from orchestration_service.application.entry_saga import EntrySagaOrchestrationService
from orchestration_service.application.exit_saga import ExitSagaOrchestrationService
from orchestration_service.application.operation_status import OperationStatusQueryService
from orchestration_service.clients.grpc.parking_command import ParkingCommandGrpcClient
from orchestration_service.clients.grpc.parking_query import ParkingQueryGrpcClient
from orchestration_service.clients.grpc.vehicle import VehicleGrpcClient
from orchestration_service.clients.grpc.zone import ZoneGrpcClient
from orchestration_service.repositories.operation import SagaOperationRepository


def build_operation_repository() -> SagaOperationRepository:
    return SagaOperationRepository()


def build_vehicle_gateway() -> VehicleGrpcClient:
    return VehicleGrpcClient()


def build_zone_gateway() -> ZoneGrpcClient:
    return ZoneGrpcClient()


def build_parking_command_gateway() -> ParkingCommandGrpcClient:
    return ParkingCommandGrpcClient()


def build_parking_query_gateway() -> ParkingQueryGrpcClient:
    return ParkingQueryGrpcClient()


def build_entry_saga_service() -> EntrySagaOrchestrationService:
    return EntrySagaOrchestrationService(
        operation_repository=build_operation_repository(),
        vehicle_gateway=build_vehicle_gateway(),
        zone_gateway=build_zone_gateway(),
        parking_command_gateway=build_parking_command_gateway(),
        parking_query_gateway=build_parking_query_gateway(),
    )


def build_exit_saga_service() -> ExitSagaOrchestrationService:
    return ExitSagaOrchestrationService(
        operation_repository=build_operation_repository(),
        parking_command_gateway=build_parking_command_gateway(),
        parking_query_gateway=build_parking_query_gateway(),
    )


def build_operation_status_query_service() -> OperationStatusQueryService:
    return OperationStatusQueryService(operation_repository=build_operation_repository())
