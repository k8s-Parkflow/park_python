from __future__ import annotations

from django.test import TestCase
from django.db import connections

from orchestration_service.models import SagaOperation
from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType


class MsaDatabaseRoutingRepositoryTests(TestCase):
    databases = "__all__"

    def test_should_persist_model_to_routed_database__when_saved_without_using_clause(self) -> None:
        """[RT-MSA-DB-01] 라우터 기반 DB 저장"""

        vehicle = Vehicle.objects.create(vehicle_num="12가3456", vehicle_type=VehicleType.General)
        operation = SagaOperation.objects.create(
            operation_id="op-001",
            saga_type="ENTRY",
            status="IN_PROGRESS",
            current_step="STEP_VALIDATE_VEHICLE",
            idempotency_key="idem-001",
        )

        self.assertEqual(vehicle._state.db, "vehicle")
        self.assertEqual(operation._state.db, "default")
        self.assertEqual(Vehicle.objects.using("vehicle").count(), 1)
        self.assertEqual(SagaOperation.objects.using("default").count(), 1)

    def test_should_isolate_service_tables_per_database__when_migrations_run(self) -> None:
        """[RT-MSA-DB-02] 서비스 테이블이 전용 DB에만 생성된다"""

        default_tables = set(connections["default"].introspection.table_names())
        vehicle_tables = set(connections["vehicle"].introspection.table_names())

        self.assertIn("VEHICLE", vehicle_tables)
        self.assertNotIn("VEHICLE", default_tables)
        self.assertIn("SAGA_OPERATION", default_tables)
