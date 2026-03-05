from __future__ import annotations

from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from parking_command_service.models.enums import ParkingHistoryStatus


class ParkingHistory(models.Model):
    history_id = models.BigAutoField(primary_key=True)
    slot = models.ForeignKey(
        "parking_command_service.ParkingSlot",
        on_delete=models.PROTECT,
        db_column="slot_id",
        related_name="parking_histories",
    )
    vehicle_num = models.CharField(max_length=20)
    status = models.CharField(
        max_length=16,
        choices=ParkingHistoryStatus.choices,
        default=ParkingHistoryStatus.PARKED,
    )
    entry_at = models.DateTimeField()
    exit_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PARKING_HISTORY"
        indexes = [
            models.Index(fields=["slot", "entry_at"], name="idx_history_slot_entry"),
            models.Index(
                fields=["vehicle_num", "exit_at"],
                name="idx_history_vehicle_exit",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle_num"],
                condition=Q(exit_at__isnull=True),
                name="uniq_active_history_per_vehicle",
            ),
            # TODO: 슬롯 기준 활성 이력 유일성 제약 추가 검토
        ]

    @classmethod
    def start(
        cls, *, slot: "ParkingSlot", vehicle_num: str, entry_at: datetime | None = None,
    ) -> "ParkingHistory":
        normalized_vehicle_num = vehicle_num.strip().upper()
        if not normalized_vehicle_num:
            raise ValidationError("차량 번호는 비어 있을 수 없습니다.")

        return cls(
            slot=slot,
            vehicle_num=normalized_vehicle_num,
            entry_at=entry_at or timezone.now(),
            status=ParkingHistoryStatus.PARKED,
        )

    def exit(self, *, exited_at: datetime | None = None) -> None:
        if self.status == ParkingHistoryStatus.EXITED:
            raise ValidationError("이미 출차 처리된 이력입니다.")

        self.status = ParkingHistoryStatus.EXITED
        self.exit_at = exited_at or timezone.now()
