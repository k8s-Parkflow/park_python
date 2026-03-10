from __future__ import annotations

from orchestration_service.clients.http import JsonHttpClient


class ParkingCommandServiceClient:
    def __init__(self, *, base_url: str = "", http_client: JsonHttpClient | None = None) -> None:
        self.base_url = base_url
        self.http_client = http_client or JsonHttpClient()

    def create_entry(self, *, operation_id: str, vehicle_num: str, slot_id: int, requested_at: str) -> dict:
        payload = self.http_client.post(
            dependency="parking-command-service",
            url=f"{self.base_url}/internal/parking-command/entries",
            payload={
                "operation_id": operation_id,
                "vehicle_num": vehicle_num,
                "slot_id": slot_id,
                "requested_at": requested_at,
            },
        )
        return self.parse_entry_response(payload)

    def cancel_entry(self, *, operation_id: str, history_id: int) -> dict:
        return self.http_client.post(
            dependency="parking-command-service",
            url=f"{self.base_url}/internal/parking-command/entries/compensations",
            payload={"operation_id": operation_id, "history_id": history_id},
        )

    def create_exit(self, *, operation_id: str, vehicle_num: str, requested_at: str) -> dict:
        payload = self.http_client.post(
            dependency="parking-command-service",
            url=f"{self.base_url}/internal/parking-command/exits",
            payload={
                "operation_id": operation_id,
                "vehicle_num": vehicle_num,
                "requested_at": requested_at,
            },
        )
        return self.parse_exit_response(payload)

    def restore_exit(self, *, operation_id: str, history_id: int) -> dict:
        return self.http_client.post(
            dependency="parking-command-service",
            url=f"{self.base_url}/internal/parking-command/exits/compensations",
            payload={"operation_id": operation_id, "history_id": history_id},
        )

    def parse_entry_response(self, payload: dict) -> dict:
        return {
            "history_id": payload["history_id"],
            "slot_id": payload["slot_id"],
            "vehicle_num": payload["vehicle_num"],
            "entry_at": payload["entry_at"],
            "status": payload["status"],
        }

    def parse_exit_response(self, payload: dict) -> dict:
        return {
            "history_id": payload["history_id"],
            "slot_id": payload["slot_id"],
            "vehicle_num": payload["vehicle_num"],
            "exit_at": payload["exit_at"],
            "status": payload["status"],
        }
