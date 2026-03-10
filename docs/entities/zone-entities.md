# zone-service 스키마

## 생성 대상 테이블

- `ZONE`
- `SLOT_TYPE`

## ZONE

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `zone_id` | bigint | N | auto increment | PK |
| `zone_name` | varchar(100) | N |  | UK |
| `created_at` | timestamp | N | auto now add |  |
| `updated_at` | timestamp | N | auto now |  |

## SLOT_TYPE

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `slot_type_id` | bigint | N | auto increment | PK |
| `type_name` | varchar(50) | N |  | UK |
| `created_at` | timestamp | N | auto now add |  |
| `updated_at` | timestamp | N | auto now |  |

## 주의

- `type_name`은 슬롯 이름이 아니라 슬롯 타입 이름이다.
- 예: `GENERAL`, `EV`, `DISABLED`
