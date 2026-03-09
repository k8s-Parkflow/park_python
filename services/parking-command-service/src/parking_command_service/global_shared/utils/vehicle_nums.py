from __future__ import annotations

import re

from django.core.exceptions import ValidationError

VEHICLE_NUM_PATTERN = re.compile(r"^\d{2,3}[가-힣]\d{4}$")


def normalize_vehicle_num(vehicle_num: str) -> str:
    # 저장과 비교는 공백/하이픈이 제거된 표준 차량 번호를 기준으로 한다.
    normalized_vehicle_num = vehicle_num.strip().upper().replace("-", "").replace(" ", "")
    if not normalized_vehicle_num:
        raise ValidationError("차량 번호는 비어 있을 수 없습니다.")
    if not VEHICLE_NUM_PATTERN.match(normalized_vehicle_num):
        raise ValidationError("지원하지 않는 차량 번호 형식입니다.")
    return normalized_vehicle_num
