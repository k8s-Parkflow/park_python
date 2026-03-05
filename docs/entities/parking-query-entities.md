# parking-query-service 엔터티 설명

## 목적

- `parking-query-service`의 조회 모델 엔터티 구조를 명확히 정의한다.
- 엔터티별 역할과 컬럼 의미를 한 번에 확인할 수 있도록 정리한다.

## 엔터티 개요

- `CURRENT_PARKING_VIEW`: 현재 주차 중인 차량의 최신 상태를 조회하기 위한 뷰 모델이다.
- `ZONE_AVAILABILITY`: 존/슬롯타입별 총 슬롯, 점유, 가용 수량을 집계한 뷰 모델이다.

## CURRENT_PARKING_VIEW

현재 주차 중 차량의 상태를 차량 번호 기준으로 1행에 유지한다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `vehicle_num` | `varchar(20)` | Y | 차량 번호 PK |
| `slot_id` | `bigint` | Y | 현재 점유 슬롯 ID |
| `zone_id` | `bigint` | Y | 현재 점유 존 ID |
| `slot_type` | `varchar(50)` | Y | 슬롯 타입명 |
| `entry_at` | `timestamp` | Y | 입차 시각 |
| `updated_at` | `timestamp` | Y | 최종 갱신 시각 |

제약/인덱스:
- PK: `vehicle_num`

## ZONE_AVAILABILITY

존/슬롯타입 조합 단위로 가용성 지표를 유지한다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `zone_id` | `bigint` | Y | 존 ID |
| `slot_type` | `varchar(50)` | Y | 슬롯 타입명 |
| `total_count` | `int` | Y | 전체 슬롯 수 |
| `occupied_count` | `int` | Y | 점유 슬롯 수 |
| `available_count` | `int` | Y | 가용 슬롯 수 (`total_count - occupied_count`) |
| `updated_at` | `timestamp` | Y | 최종 갱신 시각 |

제약/인덱스:
- 유니크 제약: `(zone_id, slot_type)` (`uniq_zone_availability_zone_slot_type`)
- 인덱스: `(zone_id, slot_type)` (`idx_zone_type`)
- 체크 제약: `available_count = total_count - occupied_count` 및 `available_count >= 0` (`chk_zone_availability_available_count`)

## 엔터티 관계

- `CURRENT_PARKING_VIEW.slot_id`는 `parking-command-service`의 슬롯 식별자와 논리적으로 연결된다.
- `ZONE_AVAILABILITY.zone_id`는 `zone-service`의 존 식별자와 논리적으로 연결된다.
