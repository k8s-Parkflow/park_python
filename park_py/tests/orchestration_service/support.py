from __future__ import annotations

from orchestration_service.application.errors import DownstreamError


class FakeVehicleGateway:
    def __init__(self, *, call_log: list[str], payload: dict | None = None, error=None) -> None:
        self.call_log = call_log
        self.payload = payload or {"vehicle_num": "12가3456", "vehicle_type": "GENERAL"}
        self.error = error

    def get_vehicle(self, *, vehicle_num: str) -> dict:
        self.call_log.append("vehicle-service")
        if self.error:
            raise self.error
        return {**self.payload, "vehicle_num": vehicle_num}


class FakeZoneGateway:
    def __init__(self, *, call_log: list[str], payload: dict | None = None, error=None) -> None:
        self.call_log = call_log
        self.payload = payload or {
            "slot_id": 7,
            "zone_id": 1,
            "slot_type": "GENERAL",
            "zone_active": True,
            "entry_allowed": True,
        }
        self.error = error

    def validate_entry_policy(self, *, slot_id: int, vehicle_type: str) -> dict:
        self.call_log.append("zone-service")
        if self.error:
            raise self.error
        return {**self.payload, "slot_id": slot_id, "vehicle_type": vehicle_type}


class FakeParkingCommandGateway:
    def __init__(
        self,
        *,
        call_log: list[str],
        entry_payload: dict | None = None,
        active_payload: dict | None = None,
        exit_payload: dict | None = None,
        validate_error=None,
        entry_error=None,
        exit_error=None,
    ) -> None:
        self.call_log = call_log
        self.entry_payload = entry_payload or {
            "history_id": 101,
            "slot_id": 7,
            "vehicle_num": "12가3456",
            "entry_at": "2026-03-10T10:00:00+09:00",
            "status": "PARKED",
        }
        self.active_payload = active_payload or {
            "history_id": 101,
            "slot_id": 7,
            "zone_id": 1,
            "slot_type": "GENERAL",
            "vehicle_num": "12가3456",
            "entry_at": "2026-03-10T10:00:00+09:00",
            "status": "PARKED",
        }
        self.exit_payload = exit_payload or {
            "history_id": 101,
            "slot_id": 7,
            "vehicle_num": "12가3456",
            "exit_at": "2026-03-10T12:00:00+09:00",
            "status": "EXITED",
        }
        self.validate_error = validate_error
        self.entry_error = entry_error
        self.exit_error = exit_error
        self.compensations: list[str] = []

    def create_entry(self, **_kwargs) -> dict:
        self.call_log.append("parking-command-service")
        if self.entry_error:
            raise self.entry_error
        return self.entry_payload

    def validate_active_parking(self, **_kwargs) -> dict:
        self.call_log.append("parking-command-service")
        if self.validate_error:
            raise self.validate_error
        return self.active_payload

    def exit_parking(self, **_kwargs) -> dict:
        self.call_log.append("parking-command-service")
        if self.exit_error:
            raise self.exit_error
        return self.exit_payload

    def compensate_entry(self, **_kwargs) -> None:
        self.compensations.append("COMPENSATE_PARKING_ENTRY")

    def compensate_exit(self, **_kwargs) -> None:
        self.compensations.append("COMPENSATE_PARKING_EXIT")


class FakeParkingQueryGateway:
    def __init__(self, *, call_log: list[str], entry_error=None, exit_error=None) -> None:
        self.call_log = call_log
        self.entry_error = entry_error
        self.exit_error = exit_error
        self.compensations: list[str] = []

    def apply_entry_projection(self, **_kwargs) -> dict:
        self.call_log.append("parking-query-service")
        if self.entry_error:
            raise self.entry_error
        return {"projected": True}

    def apply_exit_projection(self, **_kwargs) -> dict:
        self.call_log.append("parking-query-service")
        if self.exit_error:
            raise self.exit_error
        return {"projected": True}

    def compensate_entry_projection(self, **_kwargs) -> None:
        self.compensations.append("COMPENSATE_QUERY_ENTRY")

    def compensate_exit_projection(self, **_kwargs) -> None:
        self.compensations.append("COMPENSATE_QUERY_EXIT")


def validation_error(*, dependency: str, message: str) -> DownstreamError:
    return DownstreamError(
        dependency=dependency,
        error_code="not_found",
        message=message,
        status=404,
    )


def projection_error() -> DownstreamError:
    return DownstreamError(
        dependency="parking-query-service",
        error_code="projection_update_failed",
        message="parking-query-service timeout",
        status=409,
    )
