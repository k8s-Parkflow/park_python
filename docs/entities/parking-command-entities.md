# parking-command-service 엔터티 설명

## 목적

- `parking-command-service`의 핵심 쓰기 모델 엔터티 구조를 명확히 정의한다.
- 엔터티별 역할과 컬럼 의미를 한 번에 확인할 수 있도록 정리한다.

## 엔터티 개요

- `PARKING_SLOT`: 주차 슬롯 마스터 정보(슬롯 식별, 존/타입, 활성 상태)를 관리한다.
- `PARKING_HISTORY`: 차량 입차/출차 이력을 관리한다.
- `SLOT_OCCUPANCY`: 슬롯의 현재 점유 상태(실시간 상태)를 관리한다.

## PARKING_SLOT

슬롯 자체의 정보를 가진다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `slot_id` | `bigint` | Y | 슬롯 PK (자동 증가) |
| `zone_id` | `bigint` | Y | 존 식별자 (`zone_service.ZONE.zone_id` 논리 참조) |
| `slot_type_id` | `bigint` | Y | 슬롯 타입 식별자 (`zone_service.SLOT_TYPE.slot_type_id` 논리 참조) |
| `slot_code` | `varchar(50)` | Y | 존 내 슬롯 코드 |
| `is_active` | `boolean` | Y | 슬롯 활성 여부 (기본값 `true`) |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 유니크 제약: `(zone_id, slot_code)` (`uniq_slot_zone_slot_code`)

## PARKING_HISTORY

차량 단위의 주차 세션(입차 시작부터 출차 종료까지)을 나타낸다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `history_id` | `bigint` | Y | 주차 이력 PK (자동 증가) |
| `slot_id` | `bigint` | Y | 주차 슬롯 FK (`PARKING_SLOT.slot_id`) |
| `vehicle_num` | `varchar(20)` | Y | 차량 번호 (`vehicle_service.VEHICLE.vehicle_num` 논리 참조) |
| `status` | `varchar(16)` | Y | 이력 상태 (`PARKED` 또는 `EXITED`) |
| `entry_at` | `timestamp` | Y | 입차 시각 |
| `exit_at` | `timestamp` | N | 출차 시각 (`NULL`이면 활성 세션) |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 인덱스: `(slot_id, entry_at)` (`idx_history_slot_entry`)
- 인덱스: `(vehicle_num, exit_at)` (`idx_history_vehicle_exit`)
- 조건부 유니크: `unique(vehicle_num) where exit_at is null` (`uniq_active_history_per_vehicle`)

## SLOT_OCCUPANCY

슬롯의 현재 점유 상태를 1행으로 유지하는 상태 테이블이다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `slot_id` | `bigint` | Y | 슬롯 PK/FK (`PARKING_SLOT.slot_id`, 1 슬롯 = 1 점유 행) |
| `occupied` | `boolean` | Y | 점유 여부 (기본값 `false`) |
| `vehicle_num` | `varchar(20)` | N | 현재 점유 차량 번호 |
| `history_id` | `bigint` | N | 현재 점유를 나타내는 이력 FK (`PARKING_HISTORY.history_id`) |
| `occupied_at` | `timestamp` | N | 점유 시작 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 체크 제약 (`slot_occupancy_consistency`)
- `occupied = true`이면 `vehicle_num`, `history_id`, `occupied_at`는 모두 필수
- `occupied = false`이면 `vehicle_num`, `history_id`, `occupied_at`는 모두 `NULL`

## 엔터티 관계

- `PARKING_HISTORY.slot_id` -> `PARKING_SLOT.slot_id` (N:1)
- `SLOT_OCCUPANCY.slot_id` -> `PARKING_SLOT.slot_id` (1:1)
- `SLOT_OCCUPANCY.history_id` -> `PARKING_HISTORY.history_id` (N:1, 점유 상태의 현재 이력 참조)
