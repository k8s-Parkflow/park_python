from __future__ import annotations

from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from parking_command_service.domains.parking_record.domain.enums import ParkingHistoryStatus
from parking_command_service.global_shared.utils.vehicle_nums import normalize_vehicle_num


class ParkingHistory(models.Model):
    history_id = models.BigAutoField(primary_key=True)
    slot = models.ForeignKey(
        "parking_command_service.ParkingSlot",
        on_delete=models.PROTECT,
        db_column="slot_id",
        related_name="parking_histories",
    )
    zone_id = models.BigIntegerField(default=0)
    slot_type_id = models.BigIntegerField(default=0)
    slot_code = models.CharField(max_length=50, default="", db_column="slot_name")
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
            models.Index(fields=["vehicle_num", "exit_at"], name="idx_history_vehicle_exit"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle_num"],
                condition=Q(exit_at__isnull=True),
                name="uniq_active_history_per_vehicle",
            ),
            models.UniqueConstraint(
                fields=["slot"],
                condition=Q(exit_at__isnull=True),
                name="uniq_active_history_per_slot",
            ),
        ]

    @classmethod
    def start(
        cls,
        *,
        slot: "ParkingSlot",
        vehicle_num: str,
        entry_at: datetime | None = None,
        zone_id: int | None = None,
        slot_type_id: int | None = None,
        slot_code: str | None = None,
    ) -> "ParkingHistory":
        # 생성 시점에 차량 번호를 정규화해 활성 세션 유니크 조건과 비교 기준을 맞춘다.
        return cls(
            slot=slot,
            zone_id=zone_id or 0,
            slot_type_id=slot_type_id or 0,
            slot_code=slot_code or "",
            vehicle_num=normalize_vehicle_num(vehicle_num),
            entry_at=entry_at or timezone.now(),
            status=ParkingHistoryStatus.PARKED,
        )

    def save(self, *args, **kwargs) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if self.slot_id is None or self.slot is None:
            return
        if not self.zone_id or not self.slot_type_id or not self.slot_code:
            raise ValidationError("주차 이력의 슬롯 snapshot 정보가 필요합니다.")

    def exit(self, *, exited_at: datetime | None = None) -> None:
        if self.status == ParkingHistoryStatus.EXITED:
            raise ValidationError("이미 출차 처리된 이력입니다.")

        resolved_exit_at = exited_at or timezone.now()
        # 입차보다 이른 출차는 세션 시간축을 깨므로 도메인에서 차단한다.
        if resolved_exit_at < self.entry_at:
            raise ValidationError("출차 시각은 입차 시각보다 빠를 수 없습니다.")

        self.status = ParkingHistoryStatus.EXITED
        self.exit_at = resolved_exit_at

    def cancel_exit(self) -> None:
        if self.status != ParkingHistoryStatus.EXITED:
            raise ValidationError("출차 보상은 종료된 이력에만 적용할 수 있습니다.")

        self.status = ParkingHistoryStatus.PARKED
        self.exit_at = None
