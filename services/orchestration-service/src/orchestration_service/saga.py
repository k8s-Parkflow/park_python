from orchestration_service.constants import (
    COMPENSATE_PARKING_ENTRY,
    COMPENSATE_QUERY_ENTRY,
    STEP_PARKING_COMMAND_ENTRY,
    STEP_UPDATE_QUERY_ENTRY,
    STEP_UPDATE_QUERY_EXIT,
    STEP_VALIDATE_ACTIVE_PARKING,
    STEP_VALIDATE_VEHICLE,
    STEP_VALIDATE_ZONE_POLICY,
    STEP_PARKING_COMMAND_EXIT,
)


class EntrySagaDefinition:
    def steps(self) -> list[str]:
        return [
            STEP_VALIDATE_VEHICLE,
            STEP_VALIDATE_ZONE_POLICY,
            STEP_PARKING_COMMAND_ENTRY,
            STEP_UPDATE_QUERY_ENTRY,
        ]


class ExitSagaDefinition:
    def steps(self) -> list[str]:
        return [
            STEP_VALIDATE_ACTIVE_PARKING,
            STEP_PARKING_COMMAND_EXIT,
            STEP_UPDATE_QUERY_EXIT,
        ]


class CompensationPlanner:
    def build(self, *, succeeded_steps: list[str]) -> list[str]:
        compensations = []
        if STEP_UPDATE_QUERY_ENTRY in succeeded_steps:
            compensations.append(COMPENSATE_QUERY_ENTRY)
        if STEP_PARKING_COMMAND_ENTRY in succeeded_steps:
            compensations.append(COMPENSATE_PARKING_ENTRY)
        return compensations
