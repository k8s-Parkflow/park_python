# parking-query-service 엔터티 설명

## 목적

- `parking-query-service`의 조회 전용 projection 구조를 정의한다.
- 어떤 필드가 command/history snapshot에서 온 값인지와 외부 조회 계약을 위해 왜 중복 저장하는지 명확히 한다.

## 엔터티 개요

- `CURRENT_PARKING_VIEW`: 현재 주차 중 차량의 최신 위치 projection
- `ZONE_AVAILABILITY`: zone/slot_type 조합별 가용성 projection
- `PARKING_QUERY_OPERATION`: query-side projection/내부 반영 작업의 로컬 멱등 처리 결과 저장 테이블

## CURRENT_PARKING_VIEW

차량 번호 기준 1행으로 유지되는 현재 위치 projection이다.  
외부 조회 응답 품질을 위해 `zone_name`, `slot_code`, `slot_name`을 함께 저장한다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `vehicle_num` | `varchar(20)` | Y | 차량 번호 PK |
| `history_id` | `bigint` | N | projection을 만든 주차 이력 식별자 |
| `zone_id` | `bigint` | N | zone 식별자 |
| `slot_id` | `bigint` | N | slot 식별자 |
| `slot_code` | `varchar(50)` | N | 입차 당시 slot code snapshot |
| `zone_name` | `varchar(100)` | N | 입차 당시 zone name snapshot |
| `slot_name` | `varchar(50)` | N | 외부 표시용 슬롯 이름, 현재는 `slot_code`와 동일하게 투영 |
| `slot_type` | `varchar(50)` | Y | slot type name |
| `entry_at` | `timestamp` | Y | 입차 시각 |
| `updated_at` | `timestamp` | Y | projection 갱신 시각 |

운영 규칙:
- 최신 projection보다 오래된 이벤트가 들어오면 덮어쓰지 않는다.
- exit projection은 `history_id`가 현재 projection과 일치할 때만 삭제한다.
- 이 엔터티는 조회 최적화를 위한 projection이므로, 원본 truth는 `parking-command-service.PARKING_HISTORY`에 있다.

## ZONE_AVAILABILITY

zone/slot_type 조합별 총 슬롯 수, 점유 수, 가용 수를 유지하는 집계 projection이다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `id` | `bigint` | Y | 물리 PK |
| `zone_id` | `bigint` | Y | zone 식별자 |
| `slot_type` | `varchar(50)` | Y | slot type name |
| `total_count` | `int` | Y | 전체 슬롯 수 |
| `occupied_count` | `int` | Y | 점유 슬롯 수 |
| `available_count` | `int` | Y | 가용 슬롯 수 |
| `updated_at` | `timestamp` | Y | 최종 갱신 시각 |

제약/인덱스:
- 유니크 제약: `(zone_id, slot_type)` (`uniq_zone_availability_zone_slot_type`)
- 인덱스: `(zone_id, slot_type)` (`idx_zone_type`)
- 체크 제약: `available_count = total_count - occupied_count` 및 `available_count >= 0`

운영 규칙:
- 물리 PK는 `id`를 사용한다.
- 업무상 자연 키는 `(zone_id, slot_type)`이며, 실제 중복 방지도 이 조합으로 관리한다.

## PARKING_QUERY_OPERATION

query-side 내부 projection 반영 작업의 로컬 멱등 처리 결과를 저장한다.  
물리 PK는 `id`를 사용하고, 업무상 중복 방지 기준은 `(operation_id, action)` 유니크 제약으로 관리한다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `id` | `bigint` | Y | 물리 PK |
| `operation_id` | `varchar(64)` | Y | 상위 작업 식별자 |
| `action` | `varchar(64)` | Y | projection 반영 액션 이름 |
| `response_payload` | `json` | N | 재진입 시 재사용할 응답 snapshot |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 유니크 제약: `(operation_id, action)` (`uniq_parking_query_operation_action`)

운영 규칙:
- 동일 `(operation_id, action)` 재요청이면 기존 결과를 재사용한다.
- `id`는 물리 PK이고, 비즈니스 식별자는 아니다.

## 엔터티 관계

- `CURRENT_PARKING_VIEW.history_id`는 `parking-command-service.PARKING_HISTORY.history_id`를 논리 참조한다.
- `CURRENT_PARKING_VIEW.zone_id`, `ZONE_AVAILABILITY.zone_id`는 `zone-service.ZONE.zone_id`를 논리 참조한다.
- `CURRENT_PARKING_VIEW.slot_code`, `zone_name`, `slot_name`, `slot_type`는 외부 조회 응답을 위한 snapshot/projection 값이다.
