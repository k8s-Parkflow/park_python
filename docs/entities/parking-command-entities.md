# parking-command-service 스키마

## 생성 대상 테이블

- `PARKING_SLOT`
- `PARKING_HISTORY`
- `SLOT_OCCUPANCY`
- `PARKING_COMMAND_OPERATION`

## 공통 원칙

- 이 서비스 DB에서만 의미 있는 로컬 FK만 생성한다.
- `zone_id`, `slot_type_id`, `vehicle_num`은 다른 서비스 값이므로 DB FK를 만들지 않는다.
- 슬롯 식별 문자열 컬럼명은 `slot_name`으로 통일한다.

## PARKING_SLOT

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `slot_id` | bigint | N | auto increment | PK |
| `zone_id` | bigint | N |  | UK 일부 |
| `slot_type_id` | bigint | N |  |  |
| `slot_name` | varchar(50) | N |  | UK 일부 |
| `is_active` | boolean | N | `true` |  |
| `created_at` | timestamp | N | auto now add |  |
| `updated_at` | timestamp | N | auto now |  |

추가 제약:
- Unique `(zone_id, slot_name)` (`uniq_slot_zone_slot_name`)

## PARKING_HISTORY

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `history_id` | bigint | N | auto increment | PK |
| `slot_id` | bigint | N |  | FK -> `PARKING_SLOT.slot_id` |
| `vehicle_num` | varchar(20) | N |  | 조건부 UK |
| `status` | varchar(16) | N | `PARKED` |  |
| `entry_at` | timestamp | N |  |  |
| `exit_at` | timestamp | Y |  |  |
| `created_at` | timestamp | N | auto now add |  |
| `updated_at` | timestamp | N | auto now |  |

인덱스:
- `(slot_id, entry_at)` (`idx_history_slot_entry`)
- `(vehicle_num, exit_at)` (`idx_history_vehicle_exit`)

추가 제약:
- Unique `vehicle_num` where `exit_at is null` (`uniq_active_history_per_vehicle`)
- Unique `slot_id` where `exit_at is null` (`uniq_active_history_per_slot`)

## SLOT_OCCUPANCY

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `slot_id` | bigint | N |  | PK, FK -> `PARKING_SLOT.slot_id` |
| `occupied` | boolean | N | `false` |  |
| `vehicle_num` | varchar(20) | Y |  |  |
| `history_id` | bigint | Y |  | UK, FK -> `PARKING_HISTORY.history_id` |
| `occupied_at` | timestamp | Y |  |  |
| `updated_at` | timestamp | N | auto now |  |

추가 제약:
- Check `slot_occupancy_consistency`
  - `occupied = true`면 `vehicle_num`, `history_id`, `occupied_at` 모두 NOT NULL
  - `occupied = false`면 `vehicle_num`, `history_id`, `occupied_at` 모두 NULL

## PARKING_COMMAND_OPERATION

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `id` | bigint | N | auto increment | PK |
| `operation_id` | varchar(64) | N |  | UK 일부 |
| `action` | varchar(64) | N |  | UK 일부 |
| `response_payload` | json | Y |  |  |
| `created_at` | timestamp | N | auto now add |  |
| `updated_at` | timestamp | N | auto now |  |

추가 제약:
- Unique `(operation_id, action)` (`uniq_parking_command_operation_action`)

## 최종 관계 요약

- `PARKING_HISTORY.slot_id -> PARKING_SLOT.slot_id`
- `SLOT_OCCUPANCY.slot_id -> PARKING_SLOT.slot_id`
- `SLOT_OCCUPANCY.history_id -> PARKING_HISTORY.history_id`
