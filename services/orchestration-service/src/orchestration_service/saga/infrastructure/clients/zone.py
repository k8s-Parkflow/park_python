from __future__ import annotations

from orchestration_service.saga.infrastructure.clients.http import JsonHttpClient


class ZoneServiceClient:
    def __init__(self, *, base_url: str = "", http_client: JsonHttpClient | None = None) -> None:
        self.base_url = base_url
        self.http_client = http_client or JsonHttpClient()

    def get_entry_policy(self, *, slot_id: int) -> dict:
        payload = self.http_client.get(
            dependency="zone-service",
            url=f"{self.base_url}/internal/zones/slots/{slot_id}/entry-policy",
        )
        return self.parse_entry_policy_response(payload)

    def parse_entry_policy_response(self, payload: dict) -> dict:
        return {
            "slot_id": payload["slot_id"],
            "zone_id": payload["zone_id"],
            "slot_type": payload["slot_type"],
            "zone_active": payload["zone_active"],
            "entry_allowed": payload["entry_allowed"],
        }


__all__ = ["ZoneServiceClient"]
