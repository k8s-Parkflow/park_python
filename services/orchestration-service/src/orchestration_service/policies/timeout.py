class TimeoutPolicy:
    def __init__(self, *, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds

    def is_timed_out(self, *, elapsed_seconds: float) -> bool:
        return elapsed_seconds > self.timeout_seconds

