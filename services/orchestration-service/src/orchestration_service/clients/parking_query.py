class ParkingQueryServiceClient:
    def parse_projection_response(self, payload: dict) -> dict:
        return {
            "projected": payload["projected"],
            "updated_at": payload["updated_at"],
        }

