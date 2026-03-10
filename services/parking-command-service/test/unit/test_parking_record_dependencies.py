from __future__ import annotations

import sys
from pathlib import Path

from django.test import SimpleTestCase

from parking_command_service.clients.grpc.parking_query import (
    ParkingQueryGrpcProjectionWriter,
)
from parking_command_service.clients.grpc.zone import ZoneGrpcClient
from parking_command_service.clients.grpc.vehicle import VehicleGrpcClient
from parking_command_service.domains.parking_record.application.services import (
    ParkingRecordCommandService,
)
from parking_command_service.domains.parking_record.infrastructure.repositories import (
    DjangoParkingRecordRepository,
)
from parking_command_service.global_shared.application.dependencies import (
    get_parking_record_command_service,
)

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))


# 의존성 조립 단위 테스트 클래스
class ParkingRecordDependenciesUnitTests(SimpleTestCase):
    # command 서비스 기본 조립 검증
    def test_should_build_service__when_default_requested(self) -> None:
        # Given / When
        service = get_parking_record_command_service()

        # Then
        self.assertIsInstance(service, ParkingRecordCommandService)
        self.assertIsInstance(service.parking_record_repository, DjangoParkingRecordRepository)
        self.assertIsInstance(service.projection_writer, ParkingQueryGrpcProjectionWriter)
        self.assertIsInstance(service.vehicle_repository, VehicleGrpcClient)
        self.assertIsInstance(service.projection_writer.zone_lookup, ZoneGrpcClient)
