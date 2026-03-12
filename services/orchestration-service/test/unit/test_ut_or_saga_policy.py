import sys
from pathlib import Path

from django.test import SimpleTestCase


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class OrchestrationSagaPolicyTests(SimpleTestCase):
    def test_should_apply_entry_saga_step_order__when_entry_flow_is_built(self) -> None:
        """[UT-OR-SAGA-01] 입차 단계 순서 정책"""

        from orchestration_service.saga import EntrySagaDefinition

        # Given
        entry_saga = EntrySagaDefinition()

        # When
        result = entry_saga.steps()

        # Then
        self.assertEqual(
            result,
            [
                "VALIDATE_VEHICLE",
                "VALIDATE_ZONE_POLICY",
                "PARKING_COMMAND_ENTRY",
                "UPDATE_QUERY_ENTRY",
            ],
        )

    def test_should_apply_exit_saga_step_order__when_exit_flow_is_built(self) -> None:
        """[UT-OR-SAGA-02] 출차 단계 순서 정책"""

        from orchestration_service.saga import ExitSagaDefinition

        # Given
        exit_saga = ExitSagaDefinition()

        # When
        result = exit_saga.steps()

        # Then
        self.assertEqual(
            result,
            [
                "VALIDATE_ACTIVE_PARKING",
                "PARKING_COMMAND_EXIT",
                "UPDATE_QUERY_EXIT",
            ],
        )

    def test_should_run_compensation_in_reverse_order__when_last_step_fails(self) -> None:
        """[UT-OR-SAGA-03] 보상 역순 정책"""

        from orchestration_service.saga import CompensationPlanner

        # Given
        succeeded_steps = [
            "VALIDATE_VEHICLE",
            "VALIDATE_ZONE_POLICY",
            "PARKING_COMMAND_ENTRY",
            "UPDATE_QUERY_ENTRY",
        ]

        # When
        result = CompensationPlanner().build(succeeded_steps=succeeded_steps)

        # Then
        self.assertEqual(
            result,
            [
                "COMPENSATE_QUERY_ENTRY",
                "COMPENSATE_PARKING_ENTRY",
            ],
        )

    def test_should_reuse_existing_operation__when_same_idempotency_key_reenters(self) -> None:
        """[UT-OR-SAGA-04] 멱등 재진입 정책"""

        from orchestration_service.saga.domain.policies import IdempotencyPolicy

        # Given
        policy = IdempotencyPolicy()
        existing_operation = {
            "operation_id": "entry-op-001",
            "status": "COMPLETED",
        }

        # When
        result = policy.resolve(
            idempotency_key="entry-idempotency-key-001",
            existing_operation=existing_operation,
        )

        # Then
        self.assertEqual(
            result,
            {
                "reused": True,
                "operation_id": "entry-op-001",
                "status": "COMPLETED",
            },
        )

    def test_should_transition_saga_statuses__when_failure_and_compensation_occur(self) -> None:
        """[UT-OR-SAGA-05] 실패 상태 전이"""

        from orchestration_service.saga import SagaStatusMachine

        # Given
        status_machine = SagaStatusMachine(initial_status="IN_PROGRESS")

        # When
        after_failure = status_machine.fail(step_name="UPDATE_QUERY_ENTRY")
        after_compensating = status_machine.start_compensation()
        after_compensated = status_machine.complete_compensation()

        # Then
        self.assertEqual(after_failure, "FAILED")
        self.assertEqual(after_compensating, "COMPENSATING")
        self.assertEqual(after_compensated, "COMPENSATED")

    def test_should_retry_only_retryable_errors__when_retry_policy_is_evaluated(self) -> None:
        """[UT-OR-POLICY-01] 재시도 정책"""

        from orchestration_service.saga.domain.policies import RetryPolicy

        # Given
        retry_policy = RetryPolicy(max_attempts=3)

        # When
        retryable_result = retry_policy.should_retry(error_code="dependency_timeout", attempt=2)
        non_retryable_result = retry_policy.should_retry(error_code="validation_error", attempt=1)

        # Then
        self.assertTrue(retryable_result)
        self.assertFalse(non_retryable_result)

    def test_should_fail_fast_on_timeout__when_dependency_timeout_threshold_is_exceeded(
        self,
    ) -> None:
        """[UT-OR-POLICY-02] 타임아웃 정책"""

        from orchestration_service.saga.domain.policies import TimeoutPolicy

        # Given
        timeout_policy = TimeoutPolicy(timeout_seconds=3)

        # When
        result = timeout_policy.is_timed_out(elapsed_seconds=3.1)

        # Then
        self.assertTrue(result)

    def test_should_map_dependency_errors_to_gateway_response__when_downstream_failure_occurs(
        self,
    ) -> None:
        """[UT-OR-POLICY-03] 오류 매핑 정책"""

        from orchestration_service.saga.domain.policies import GatewayErrorMapper

        # Given
        error_mapper = GatewayErrorMapper()

        # When
        result = error_mapper.map(
            dependency="parking-query-service",
            status_code=409,
            error_code="projection_update_failed",
        )

        # Then
        self.assertEqual(
            result,
            {
                "status": 409,
                "code": "conflict",
                "details": {
                    "dependency": "parking-query-service",
                    "error_code": "projection_update_failed",
                },
            },
        )
