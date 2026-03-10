# zone-service 엔터티 설명

## 목적

- `zone-service`의 마스터 데이터 엔터티 구조를 명확히 정의한다.
- 엔터티별 역할과 컬럼 의미를 한 번에 확인할 수 있도록 정리한다.

## 엔터티 개요

- `ZONE`: 주차 존의 기본 정보를 관리한다.
- `SLOT_TYPE`: 슬롯 타입 마스터 정보를 관리한다.

## ZONE

주차 존의 식별/명칭을 나타내는 마스터 엔터티다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `zone_id` | `bigint` | Y | 존 PK (자동 증가) |
| `zone_name` | `varchar(100)` | Y | 존 이름 (유니크) |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 유니크 제약: `zone_name`

## SLOT_TYPE

슬롯 분류(예: 일반/전기차 등)의 기준이 되는 타입 엔터티다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `slot_type_id` | `bigint` | Y | 슬롯 타입 PK (자동 증가) |
| `type_name` | `varchar(50)` | Y | 슬롯 타입명 (유니크) |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 수정 시각 |

제약/인덱스:
- 유니크 제약: `type_name`

## 엔터티 관계

- `ZONE`와 `SLOT_TYPE` 사이에 직접 FK 관계는 없다.
- 각 식별자는 다른 서비스(예: parking-command-service, parking-query-service)에서 논리 참조로 사용된다.
