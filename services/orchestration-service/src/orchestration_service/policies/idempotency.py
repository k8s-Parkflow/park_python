class IdempotencyPolicy:
    def resolve(self, *, idempotency_key: str, existing_operation) -> dict:
        if existing_operation is None:
            return {"reused": False, "idempotency_key": idempotency_key}

        return {
            "reused": True,
            "operation_id": existing_operation["operation_id"],
            "status": existing_operation["status"],
        }
