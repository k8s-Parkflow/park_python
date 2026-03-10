class ZoneServiceClient:
    def parse_entry_policy_response(self, payload: dict) -> dict:
        return {
            "slot_id": payload["slot_id"],
            "zone_id": payload["zone_id"],
            "slot_type": payload["slot_type"],
            "zone_active": payload["zone_active"],
            "entry_allowed": payload["entry_allowed"],
        }
