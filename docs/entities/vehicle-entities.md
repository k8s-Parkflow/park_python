# vehicle-service 스키마

## 생성 대상 테이블

- `VEHICLE`

## VEHICLE

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `vehicle_num` | varchar(20) | N |  | PK |
| `vehicle_type` | varchar(16) | N |  |  |
| `created_at` | timestamp | N | auto now add |  |
| `updated_at` | timestamp | N | auto now |  |

허용 값:
- `vehicle_type`: `GENERAL`, `EV`, `DISABLED`
