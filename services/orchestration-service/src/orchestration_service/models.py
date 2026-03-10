from django.db import models


class SagaOperation(models.Model):
    operation_id = models.CharField(max_length=64, primary_key=True)
    saga_type = models.CharField(max_length=16)
    status = models.CharField(max_length=32)
    idempotency_key = models.CharField(max_length=128)
    current_step = models.CharField(max_length=64, null=True, blank=True)
    failed_step = models.CharField(max_length=64, null=True, blank=True)
    history_id = models.BigIntegerField(null=True, blank=True)
    vehicle_num = models.CharField(max_length=20, null=True, blank=True)
    slot_id = models.BigIntegerField(null=True, blank=True)
    last_error_code = models.CharField(max_length=64, null=True, blank=True)
    last_error_message = models.CharField(max_length=255, null=True, blank=True)
    response_payload = models.JSONField(null=True, blank=True)
    error_status = models.IntegerField(null=True, blank=True)
    error_payload = models.JSONField(null=True, blank=True)
    compensation_attempts = models.IntegerField(default=0)
    completed_compensations = models.JSONField(default=list, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "SAGA_OPERATION"
        constraints = [
            models.UniqueConstraint(
                fields=["saga_type", "idempotency_key"],
                name="uniq_saga_operation_type_idempotency_key",
            ),
        ]
