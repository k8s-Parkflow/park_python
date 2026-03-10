class EntrySagaDefinition:
    def steps(self) -> list[str]:
        return [
            "VALIDATE_VEHICLE",
            "VALIDATE_ZONE_POLICY",
            "PARKING_COMMAND_ENTRY",
            "UPDATE_QUERY_ENTRY",
        ]


class ExitSagaDefinition:
    def steps(self) -> list[str]:
        return [
            "VALIDATE_ACTIVE_PARKING",
            "PARKING_COMMAND_EXIT",
            "UPDATE_QUERY_EXIT",
        ]


class CompensationPlanner:
    COMPENSATION_MAP = {
        "PARKING_COMMAND_ENTRY": "COMPENSATE_PARKING_ENTRY",
        "UPDATE_QUERY_ENTRY": "COMPENSATE_QUERY_ENTRY",
        "PARKING_COMMAND_EXIT": "COMPENSATE_PARKING_EXIT",
        "UPDATE_QUERY_EXIT": "COMPENSATE_QUERY_EXIT",
    }

    def build(self, *, succeeded_steps: list[str]) -> list[str]:
        compensations: list[str] = []
        for step in reversed(succeeded_steps):
            compensation_step = self.COMPENSATION_MAP.get(step)
            if compensation_step is not None:
                compensations.append(compensation_step)
        return compensations


class SagaStatusMachine:
    def __init__(self, *, initial_status: str) -> None:
        self.status = initial_status

    def fail(self, *, step_name: str) -> str:
        self.status = "FAILED"
        return self.status

    def start_compensation(self) -> str:
        self.status = "COMPENSATING"
        return self.status

    def complete_compensation(self) -> str:
        self.status = "COMPENSATED"
        return self.status
