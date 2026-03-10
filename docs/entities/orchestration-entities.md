# orchestration-service 스키마

## 생성 대상 테이블

- `SAGA_OPERATION`

## SAGA_OPERATION

| 컬럼명 | 타입 | NULL | 기본값 | 키/제약 |
| --- | --- | --- | --- | --- |
| `operation_id` | varchar(64) | N |  | PK |
| `saga_type` | varchar(16) | N |  | UK 일부 |
| `status` | varchar(32) | N |  |  |
| `idempotency_key` | varchar(128) | N |  | UK 일부 |
| `current_step` | varchar(64) | Y |  |  |
| `failed_step` | varchar(64) | Y |  |  |
| `history_id` | bigint | Y |  |  |
| `vehicle_num` | varchar(20) | Y |  |  |
| `slot_id` | bigint | Y |  |  |
| `last_error_code` | varchar(64) | Y |  |  |
| `last_error_message` | varchar(255) | Y |  |  |
| `response_payload` | json | Y |  |  |
| `error_status` | int | Y |  |  |
| `error_payload` | json | Y |  |  |
| `compensation_attempts` | int | N | `0` |  |
| `completed_compensations` | json | N | `[]` |  |
| `next_retry_at` | timestamp | Y |  |  |
| `expires_at` | timestamp | Y |  |  |
| `cancelled_at` | timestamp | Y |  |  |
| `created_at` | timestamp | N | auto now add |  |
| `updated_at` | timestamp | N | auto now |  |

추가 제약:
- Unique `(saga_type, idempotency_key)` (`uniq_saga_operation_type_idempotency_key`)

## 주의

- 이 테이블은 사가 상태 저장용이다.
- `history_id`, `vehicle_num`, `slot_id`는 모두 논리 참조 값이다.
