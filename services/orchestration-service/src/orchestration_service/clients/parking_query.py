from __future__ import annotations

from urllib.parse import quote

from orchestration_service.clients.http import JsonHttpClient


class ParkingQueryServiceClient:
    def __init__(self, *, base_url: str = "", http_client: JsonHttpClient | None = None) -> None:
        self.base_url = base_url
        self.http_client = http_client or JsonHttpClient()

    def get_current_parking(self, *, vehicle_num: str) -> dict:
        return self.http_client.get(
            dependency="parking-query-service",
            url=f"{self.base_url}/internal/parking-query/current-parking/{quote(vehicle_num, safe='')}",
        )

    def project_entry(
        self,
        *,
        operation_id: str,
        vehicle_num: str,
        slot_id: int,
        zone_id: int,
        slot_type: str,
        entry_at: str,
    ) -> dict:
        payload = self.http_client.post(
            dependency="parking-query-service",
            url=f"{self.base_url}/internal/parking-query/entries",
            payload={
                "operation_id": operation_id,
                "vehicle_num": vehicle_num,
                "slot_id": slot_id,
                "zone_id": zone_id,
                "slot_type": slot_type,
                "entry_at": entry_at,
            },
        )
        return self.parse_projection_response(payload)

    def revert_entry(self, *, operation_id: str, vehicle_num: str) -> dict:
        return self.http_client.post(
            dependency="parking-query-service",
            url=f"{self.base_url}/internal/parking-query/entries/compensations",
            payload={"operation_id": operation_id, "vehicle_num": vehicle_num},
        )

    def project_exit(self, *, operation_id: str, vehicle_num: str) -> dict:
        payload = self.http_client.post(
            dependency="parking-query-service",
            url=f"{self.base_url}/internal/parking-query/exits",
            payload={"operation_id": operation_id, "vehicle_num": vehicle_num},
        )
        return self.parse_projection_response(payload)

    def restore_exit(
        self,
        *,
        operation_id: str,
        vehicle_num: str,
        slot_id: int,
        zone_id: int,
        slot_type: str,
        entry_at: str,
    ) -> dict:
        return self.http_client.post(
            dependency="parking-query-service",
            url=f"{self.base_url}/internal/parking-query/exits/compensations",
            payload={
                "operation_id": operation_id,
                "vehicle_num": vehicle_num,
                "slot_id": slot_id,
                "zone_id": zone_id,
                "slot_type": slot_type,
                "entry_at": entry_at,
            },
        )

    def parse_projection_response(self, payload: dict) -> dict:
        result = {"projected": payload["projected"]}
        if "updated_at" in payload:
            result["updated_at"] = payload["updated_at"]
        return result
