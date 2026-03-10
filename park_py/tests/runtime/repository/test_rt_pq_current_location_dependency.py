from django.test import SimpleTestCase


class ParkingQueryCurrentLocationDependencyRuntimeTests(SimpleTestCase):
    def test_should_wire_vehicle_grpc_client__when_building_current_location_service(self) -> None:
        """[RT-PQ-LOC-01] current-location 의존성 wiring"""

        from parking_query_service.clients.grpc.vehicle import VehicleGrpcClient
        from parking_query_service.dependencies import build_current_location_service

        service = build_current_location_service()

        self.assertIsInstance(service._vehicle_lookup, VehicleGrpcClient)
