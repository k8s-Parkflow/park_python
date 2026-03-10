class ParkingQueryGrpcClient:
    def apply_entry_projection(self, **_kwargs):
        raise NotImplementedError

    def apply_exit_projection(self, **_kwargs):
        raise NotImplementedError

    def compensate_entry_projection(self, **_kwargs):
        raise NotImplementedError

    def compensate_exit_projection(self, **_kwargs):
        raise NotImplementedError
