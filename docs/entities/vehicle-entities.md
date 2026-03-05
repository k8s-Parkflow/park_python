# vehicle-service 엔터티 설명

## 목적

- `vehicle-service`의 차량 마스터 엔터티 구조를 명확히 정의한다.
- 엔터티 컬럼 의미를 한 번에 확인할 수 있도록 정리한다.

## 엔터티 개요

- `VEHICLE`: 차량 번호를 식별자로 사용하는 차량 마스터 정보다.

## VEHICLE

차량의 고유 번호와 차량 타입을 관리하는 엔터티다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `vehicle_num` | `varchar(20)` | Y | 차량 번호 PK |
| `vehicle_type` | `varchar(16)` | Y | 차량 타입 enum (`GENERAL`, `EV`, `DISABLED`) |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- PK: `vehicle_num`
- `vehicle_type`은 `VehicleType` enum으로 제한된다.

enum 정의:
- `services/vehicle-service/src/vehicle_service/models/enums.py`의 `VehicleType` 사용

## 엔터티 관계

- `VEHICLE`는 다른 서비스에서 차량 번호 기준 논리 참조로 사용된다.
