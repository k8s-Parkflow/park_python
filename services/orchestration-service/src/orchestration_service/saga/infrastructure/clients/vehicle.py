from __future__ import annotations

from urllib.parse import quote

from orchestration_service.saga.infrastructure.clients.http import JsonHttpClient


class VehicleServiceClient:
    def __init__(self, *, base_url: str = "", http_client: JsonHttpClient | None = None) -> None:
        self.base_url = base_url
        self.http_client = http_client or JsonHttpClient()

    def get_vehicle(self, *, vehicle_num: str) -> dict:
        payload = self.http_client.get(
            dependency="vehicle-service",
            url=f"{self.base_url}/internal/vehicles/{quote(vehicle_num, safe='')}",
        )
        return self.parse_lookup_response(payload)

    def parse_lookup_response(self, payload: dict) -> dict:
        return {
            "vehicle_num": payload["vehicle_num"],
            "vehicle_type": payload["vehicle_type"],
        }


__all__ = ["VehicleServiceClient"]
