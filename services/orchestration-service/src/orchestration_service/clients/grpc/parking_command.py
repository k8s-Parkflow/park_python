class ParkingCommandGrpcClient:
    def create_entry(self, **_kwargs):
        raise NotImplementedError

    def validate_active_parking(self, **_kwargs):
        raise NotImplementedError

    def exit_parking(self, **_kwargs):
        raise NotImplementedError

    def compensate_entry(self, **_kwargs):
        raise NotImplementedError

    def compensate_exit(self, **_kwargs):
        raise NotImplementedError
