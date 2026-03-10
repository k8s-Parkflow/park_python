from __future__ import annotations

from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from parking_command_service.global_shared.utils.vehicle_nums import normalize_vehicle_num


class SlotOccupancy(models.Model):
    """Current occupancy state keyed by the command-side lock anchor row."""

    slot = models.OneToOneField(
        "parking_command_service.ParkingSlot",
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="slot_id",
        related_name="occupancy",
    )
    occupied = models.BooleanField(default=False)
    vehicle_num = models.CharField(max_length=20, null=True, blank=True)

    history = models.OneToOneField(
        "parking_command_service.ParkingHistory",
        on_delete=models.PROTECT,
        db_column="history_id",
        null=True,
        blank=True,
        related_name="slot_occupancy",
    )

    occupied_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "SLOT_OCCUPANCY"
        constraints = [
            models.CheckConstraint(
                check=(
                    (
                        Q(occupied=True)
                        & Q(vehicle_num__isnull=False)
                        & Q(history__isnull=False)
                        & Q(occupied_at__isnull=False)
                    )
                    | (
                        Q(occupied=False)
                        & Q(vehicle_num__isnull=True)
                        & Q(history__isnull=True)
                        & Q(occupied_at__isnull=True)
                    )
                ),
                name="slot_occupancy_consistency",
            ),
        ]

    def occupy(
        self,
        *,
        vehicle_num: str,
        history: "ParkingHistory",
        occupied_at: datetime | None = None,
        enforce_slot_active: bool = True,
    ) -> None:
        self._validate_can_occupy(enforce_slot_active=enforce_slot_active)
        # 점유 상태는 차량 번호, 현재 이력, 점유 시각이 항상 함께 움직여야 한다.
        self._mark_occupied(
            vehicle_num=normalize_vehicle_num(vehicle_num),
            history=history,
            occupied_at=occupied_at,
        )
        self.clean()

    def release(self) -> None:
        self._validate_can_release()
        self._mark_released()
        self.clean()

    def restore(
        self, *, vehicle_num: str, history: "ParkingHistory", occupied_at: datetime | None = None,
    ) -> None:
        if self.occupied:
            raise ValidationError("이미 점유 중인 슬롯입니다.")
        self._mark_occupied(
            vehicle_num=normalize_vehicle_num(vehicle_num),
            history=history,
            occupied_at=occupied_at,
        )
        self.clean()

    def clean(self) -> None:
        super().clean()
        if self.occupied and not self.vehicle_num:
            raise ValidationError("차량 번호는 비어 있을 수 없습니다.")
        # 점유가 참조하는 활성 이력은 반드시 같은 슬롯 소속이어야 한다.
        if self.history and self.history.slot_id != self.slot_id:
            raise ValidationError("주차 이력의 슬롯 정보가 일치하지 않습니다.")

    def _validate_can_occupy(self, *, enforce_slot_active: bool = True) -> None:
        if self.occupied:
            raise ValidationError("이미 점유 중인 슬롯입니다.")
        if enforce_slot_active and not self.slot.is_active:
            raise ValidationError("비활성화된 슬롯입니다.")

    def _validate_can_release(self) -> None:
        if not self.occupied:
            raise ValidationError("점유 중인 슬롯이 아닙니다.")

    def _mark_occupied(
        self, *, vehicle_num: str, history: "ParkingHistory", occupied_at: datetime | None,
    ) -> None:
        self.occupied = True
        self.vehicle_num = vehicle_num
        self.history = history
        self.occupied_at = occupied_at or timezone.now()

    def _mark_released(self) -> None:
        self.occupied = False
        self.vehicle_num = None
        self.history = None
        self.occupied_at = None
