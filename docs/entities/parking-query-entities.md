# parking-query-service 스키마

## 생성 대상 테이블

- `CURRENT_PARKING_VIEW`
- `ZONE_AVAILABILITY`
- `PARKING_QUERY_OPERATION`

## 공통 원칙

- 이 서비스는 projection 저장소라 로컬 FK를 만들지 않는다.
- `vehicle_num`, `history_id`, `zone_id`, `slot_id`는 모두 논리 참조 값이다.
- 슬롯 식별 문자열은 `slot_name` 하나만 사용한다.

## CURRENT_PARKING_VIEW

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `vehicle_num` | varchar(20) | N |  | PK |
| `history_id` | bigint | Y |  |  |
| `zone_id` | bigint | Y |  |  |
| `slot_id` | bigint | Y |  |  |
| `zone_name` | varchar(100) | Y |  |  |
| `slot_name` | varchar(50) | Y |  |  |
| `slot_type` | varchar(50) | N |  |  |
| `entry_at` | timestamp | N |  |  |
| `updated_at` | timestamp | N | auto now |  |

## ZONE_AVAILABILITY

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `id` | bigint | N | auto increment | PK |
| `zone_id` | bigint | N |  | UK 일부, IDX |
| `slot_type` | varchar(50) | N |  | UK 일부, IDX |
| `total_count` | int | N |  |  |
| `occupied_count` | int | N |  |  |
| `available_count` | int | N |  | check |
| `updated_at` | timestamp | N | auto now |  |

인덱스:
- `(zone_id, slot_type)` (`idx_zone_type`)

추가 제약:
- Unique `(zone_id, slot_type)` (`uniq_zone_availability_zone_slot_type`)
- Check `available_count = total_count - occupied_count AND available_count >= 0` (`chk_zone_availability_available_count`)

## PARKING_QUERY_OPERATION

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `id` | bigint | N | auto increment | PK |
| `operation_id` | varchar(64) | N |  | UK 일부 |
| `action` | varchar(64) | N |  | UK 일부 |
| `response_payload` | json | Y |  |  |
| `created_at` | timestamp | N | auto now add |  |
| `updated_at` | timestamp | N | auto now |  |

추가 제약:
- Unique `(operation_id, action)` (`uniq_parking_query_operation_action`)

## 최종 관계 요약

- 로컬 FK 없음
- `zone_id`, `slot_type` 조합으로 집계 projection 관리
