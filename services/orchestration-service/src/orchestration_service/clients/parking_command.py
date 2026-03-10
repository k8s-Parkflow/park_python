class ParkingCommandServiceClient:
    def parse_entry_response(self, payload: dict) -> dict:
        return {
            "history_id": payload["history_id"],
            "slot_id": payload["slot_id"],
            "vehicle_num": payload["vehicle_num"],
            "entry_at": payload["entry_at"],
            "status": payload["status"],
        }

