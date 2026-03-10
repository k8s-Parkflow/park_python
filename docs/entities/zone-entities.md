# zone-service 엔터티 설명

## 목적

- `zone-service`의 슬롯 메타데이터 마스터 구조를 정의한다.
- `parking-command-service`와의 책임 분리 기준에서 어떤 데이터가 authoritative source인지 명확히 한다.

## 엔터티 개요

- `ZONE`: 주차 구역 마스터
- `SLOT_TYPE`: 슬롯 타입 마스터
- `ZONE_PARKING_SLOT`: 슬롯 메타데이터 마스터

## ZONE

주차 구역의 기본 식별과 활성 상태를 나타낸다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `zone_id` | `bigint` | Y | zone PK |
| `zone_name` | `varchar(100)` | Y | zone 이름 |
| `is_active` | `boolean` | Y | zone 활성 여부 |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 유니크 제약: `zone_name`

## SLOT_TYPE

입차 정책 판정에 사용되는 슬롯 타입 마스터다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `slot_type_id` | `bigint` | Y | slot type PK |
| `type_name` | `varchar(50)` | Y | slot type 이름 |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 유니크 제약: `type_name`

## ZONE_PARKING_SLOT

슬롯 메타데이터의 authoritative source다.  
입차 가능 여부 판단에 필요한 slot의 zone, type, code, active 상태를 모두 가진다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `slot_id` | `bigint` | Y | slot PK |
| `zone_id` | `bigint` | Y | `ZONE.zone_id` FK |
| `slot_type_id` | `bigint` | Y | `SLOT_TYPE.slot_type_id` FK |
| `slot_code` | `varchar(50)` | Y | 외부/운영 식별용 slot code |
| `is_active` | `boolean` | Y | slot 활성 여부 |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

운영 규칙:
- `ValidateEntryPolicy`는 이 엔터티와 `ZONE`, `SLOT_TYPE`를 기준으로 payload를 만든다.
- `parking-command-service.PARKING_SLOT`은 이 엔터티의 실행용 mirror일 뿐 원본이 아니다.

## 엔터티 관계

- `ZONE_PARKING_SLOT.zone_id` -> `ZONE.zone_id` (N:1)
- `ZONE_PARKING_SLOT.slot_type_id` -> `SLOT_TYPE.slot_type_id` (N:1)

