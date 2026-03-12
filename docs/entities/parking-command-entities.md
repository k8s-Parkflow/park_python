# parking-command-service 엔터티 설명

## 목적

- `parking-command-service`의 쓰기 모델과 command-side 현재 상태 모델을 정의한다.
- `zone-service`와의 책임 분리 이후, 어떤 데이터가 원본이고 어떤 데이터가 로컬 실행용인지 명확히 정리한다.

## 엔터티 개요

- `PARKING_COMMAND_OPERATION`: command-side 로컬 멱등 처리 결과 저장 테이블이다.
- `PARKING_SLOT`: command-side lock anchor. 점유 전이와 동시성 제어를 위한 최소 슬롯 행이다.
- `PARKING_HISTORY`: 입차부터 출차까지의 주차 세션 이력이다.
- `SLOT_OCCUPANCY`: 슬롯 현재 점유 상태를 나타내는 현재 상태 테이블이다.

## PARKING_COMMAND_OPERATION

입차/출차/보상 같은 command-side write action의 로컬 멱등 처리 결과를 저장한다.  
물리 PK는 `id`를 사용하고, 업무상 중복 방지 기준은 `(operation_id, action)` 유니크 제약으로 관리한다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `id` | `bigint` | Y | 물리 PK |
| `operation_id` | `varchar(64)` | Y | 오케스트레이션에서 전달한 작업 식별자 |
| `action` | `varchar(64)` | Y | 로컬 멱등성을 구분하는 액션 이름 |
| `response_payload` | `json` | N | 재진입 시 재사용할 응답 snapshot |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 유니크 제약: `(operation_id, action)` (`uniq_parking_command_operation_action`)

운영 규칙:
- 동일 `(operation_id, action)` 재요청이면 기존 결과를 재사용한다.
- `id`는 참조 안정성을 위한 물리 PK이고, 비즈니스 식별자는 아니다.

## PARKING_SLOT

`parking-command-service`의 `PARKING_SLOT`은 슬롯 메타데이터 마스터가 아니다.  
실제 슬롯 메타데이터 원본은 `zone-service.ZONE_PARKING_SLOT`이며, 이 테이블은 `slot_id` 단위 잠금과 점유 상태 전이를 위해 유지된다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `slot_id` | `bigint` | Y | lock anchor PK |
| `zone_id` | `bigint` | Y | `zone-service` 기준 zone 식별자의 로컬 mirror |
| `slot_name` (`slot_code`) | `varchar(50)` | Y | 사용자 식별용 슬롯 코드의 로컬 mirror |
| `is_active` | `boolean` | Y | 운영 동기화용 활성 상태 mirror |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 유니크 제약: `(zone_id, slot_name)` (`uniq_slot_zone_slot_name`)

운영 규칙:
- 이 테이블은 `zone-service` 원본 슬롯을 `sync_slot_lock_anchors`로 동기화해 유지한다.
- strict/trusted 입차 모두 슬롯 메타데이터 판정은 `zone-service` 응답을 기준으로 한다.
- 이 테이블의 주 용도는 `slot_id` 기반 row lock과 `SLOT_OCCUPANCY` 연결이다.

## PARKING_HISTORY

차량 단위 주차 세션 이력이다.  
입차 시점의 슬롯 snapshot을 함께 보존하므로, 이후 `zone-service` 슬롯 마스터가 바뀌어도 history와 projection은 입차 당시 정보를 유지한다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `history_id` | `bigint` | Y | 주차 이력 PK |
| `slot_id` | `bigint` | Y | `PARKING_SLOT.slot_id` FK |
| `zone_id` | `bigint` | Y | 입차 당시 zone snapshot |
| `slot_type_id` | `bigint` | Y | 입차 당시 slot type snapshot |
| `slot_name` (`slot_code`) | `varchar(50)` | Y | 입차 당시 slot code snapshot |
| `vehicle_num` | `varchar(20)` | Y | 정규화된 차량 번호 |
| `status` | `varchar(16)` | Y | `PARKED` 또는 `EXITED` |
| `entry_at` | `timestamp` | Y | 입차 시각 |
| `exit_at` | `timestamp` | N | 출차 시각 |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 인덱스: `(slot_id, entry_at)` (`idx_history_slot_entry`)
- 인덱스: `(vehicle_num, exit_at)` (`idx_history_vehicle_exit`)
- 조건부 유니크: `unique(vehicle_num) where exit_at is null` (`uniq_active_history_per_vehicle`)
- 조건부 유니크: `unique(slot_id) where exit_at is null` (`uniq_active_history_per_slot`)

도메인 규칙:
- `zone_id`, `slot_type_id`, `slot_code` snapshot이 없으면 저장할 수 없다.
- `vehicle_num`은 저장 전에 정규화된다.
- 출차 시각은 입차 시각보다 이를 수 없다.

## SLOT_OCCUPANCY

슬롯 현재 점유 상태를 1행으로 유지하는 현재 상태 테이블이다.  
단순 검증용 테이블이 아니라, 점유 상태 전이와 동시성 제어의 기준 상태다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `slot_id` | `bigint` | Y | PK/FK, `PARKING_SLOT.slot_id` |
| `occupied` | `boolean` | Y | 점유 여부 |
| `vehicle_num` | `varchar(20)` | N | 현재 점유 차량 번호 |
| `history_id` | `bigint` | N | 현재 점유를 대표하는 `PARKING_HISTORY.history_id` |
| `occupied_at` | `timestamp` | N | 현재 점유 시작 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 체크 제약 (`slot_occupancy_consistency`)
  - `occupied = true`이면 `vehicle_num`, `history_id`, `occupied_at`는 모두 필수
  - `occupied = false`이면 `vehicle_num`, `history_id`, `occupied_at`는 모두 `NULL`
- `history_id`는 `OneToOne`로 유지된다.

도메인 규칙:
- 점유 상태는 `occupy`, `release`, `restore`로만 전이한다.
- `history.slot_id`와 `occupancy.slot_id`가 다르면 저장할 수 없다.
- trusted 내부 경로에서는 `slot.is_active` 재검증을 우회할 수 있지만, 점유 row lock은 항상 이 엔터티를 통해 잡는다.

## 엔터티 관계

- `PARKING_HISTORY.slot_id` -> `PARKING_SLOT.slot_id` (N:1)
- `SLOT_OCCUPANCY.slot_id` -> `PARKING_SLOT.slot_id` (1:1)
- `SLOT_OCCUPANCY.history_id` -> `PARKING_HISTORY.history_id` (1:1)

## 서비스 경계 메모

- 슬롯 메타데이터 원본:
  - `zone-service.ZONE_PARKING_SLOT`
- 주차 기록 원본:
  - `parking-command-service.PARKING_HISTORY`
- 현재 점유 원본:
  - `parking-command-service.SLOT_OCCUPANCY`
