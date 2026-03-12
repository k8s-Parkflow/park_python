from django.test import SimpleTestCase


class ParkingQueryCurrentLocationDependencyRuntimeTests(SimpleTestCase):
    def test_should_wire_vehicle_grpc_client__when_building_current_location_service(self) -> None:
        """[RT-PQ-LOC-01] current-location 의존성 wiring"""

        from parking_query_service.parking_view.bootstrap import build_get_current_location
        from parking_query_service.parking_view.infrastructure.clients.grpc.vehicle import (
            VehicleGrpcClient,
        )

        service = build_get_current_location()

        self.assertIsInstance(service._vehicle_lookup, VehicleGrpcClient)
