from django.db import models


class SagaOperation(models.Model):
    operation_id = models.CharField(max_length=64, primary_key=True)
    idempotency_key = models.CharField(max_length=128, unique=True)
    saga_type = models.CharField(max_length=16)
    status = models.CharField(max_length=32)
    current_step = models.CharField(max_length=64, blank=True)
    history_id = models.BigIntegerField(null=True, blank=True)
    vehicle_num = models.CharField(max_length=20, blank=True)
    slot_id = models.BigIntegerField(null=True, blank=True)
    last_error_code = models.CharField(max_length=64, blank=True)
    last_error_message = models.TextField(blank=True)
    result_snapshot = models.JSONField(default=dict, blank=True)
    completed_compensations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "SAGA_OPERATION"
