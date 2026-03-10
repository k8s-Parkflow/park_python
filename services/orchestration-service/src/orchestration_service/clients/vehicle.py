class VehicleServiceClient:
    def parse_lookup_response(self, payload: dict) -> dict:
        return {
            "vehicle_num": payload["vehicle_num"],
            "vehicle_type": payload["vehicle_type"],
        }

