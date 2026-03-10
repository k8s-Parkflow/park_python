class RetryPolicy:
    RETRYABLE_ERROR_CODES = {"dependency_timeout"}

    def __init__(self, *, max_attempts: int) -> None:
        self.max_attempts = max_attempts

    def should_retry(self, *, error_code: str, attempt: int) -> bool:
        return error_code in self.RETRYABLE_ERROR_CODES and attempt < self.max_attempts

