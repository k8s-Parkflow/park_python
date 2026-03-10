from django.test import SimpleTestCase


class ParkingCommandDependencyRuntimeTests(SimpleTestCase):
    def test_should_wire_vehicle_grpc_client__when_building_http_command_service(self) -> None:
        """[RT-PC-DEP-01] HTTP command service vehicle wiring"""

        from parking_command_service.clients.grpc.vehicle import VehicleGrpcClient
        from parking_command_service.global_shared.application.dependencies import (
            get_parking_record_command_service,
        )

        service = get_parking_record_command_service()

        self.assertIsInstance(service.vehicle_repository, VehicleGrpcClient)

    def test_should_wire_vehicle_grpc_client__when_building_grpc_application(self) -> None:
        """[RT-PC-DEP-02] gRPC application vehicle wiring"""

        from parking_command_service.clients.grpc.vehicle import VehicleGrpcClient
        from parking_command_service.grpc.application import ParkingCommandGrpcApplicationService

        service = ParkingCommandGrpcApplicationService()

        self.assertIsInstance(service.command_service.vehicle_repository, VehicleGrpcClient)
