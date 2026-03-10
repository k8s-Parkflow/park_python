from __future__ import annotations

from django.test import SimpleTestCase

from orchestration_service.policies.idempotency import IdempotencyPolicy
from orchestration_service.saga import CompensationPlanner, EntrySagaDefinition, ExitSagaDefinition


class OrchestrationSagaPolicyTests(SimpleTestCase):
    def test_should_apply_entry_saga_step_order__when_entry_flow_is_built(self) -> None:
        """[UT-OR-SAGA-01] 입차 단계 순서 정책"""

        self.assertEqual(
            EntrySagaDefinition().steps(),
            [
                "VALIDATE_VEHICLE",
                "VALIDATE_ZONE_POLICY",
                "PARKING_COMMAND_ENTRY",
                "UPDATE_QUERY_ENTRY",
            ],
        )

    def test_should_apply_exit_saga_step_order__when_exit_flow_is_built(self) -> None:
        """[UT-OR-SAGA-02] 출차 단계 순서 정책"""

        self.assertEqual(
            ExitSagaDefinition().steps(),
            [
                "VALIDATE_ACTIVE_PARKING",
                "PARKING_COMMAND_EXIT",
                "UPDATE_QUERY_EXIT",
            ],
        )

    def test_should_run_compensation_in_reverse_order__when_last_step_fails(self) -> None:
        """[UT-OR-SAGA-03] 보상 역순 정책"""

        result = CompensationPlanner().build(
            succeeded_steps=[
                "VALIDATE_VEHICLE",
                "VALIDATE_ZONE_POLICY",
                "PARKING_COMMAND_ENTRY",
                "UPDATE_QUERY_ENTRY",
            ]
        )

        self.assertEqual(
            result,
            ["COMPENSATE_QUERY_ENTRY", "COMPENSATE_PARKING_ENTRY"],
        )

    def test_should_reuse_existing_operation__when_same_idempotency_key_reenters(self) -> None:
        """[UT-OR-SAGA-04] 멱등 재진입 정책"""

        result = IdempotencyPolicy().resolve(
            idempotency_key="entry-idempotency-key-001",
            existing_operation={
                "operation_id": "entry-op-001",
                "status": "COMPLETED",
            },
        )

        self.assertEqual(
            result,
            {
                "reused": True,
                "operation_id": "entry-op-001",
                "status": "COMPLETED",
            },
        )
