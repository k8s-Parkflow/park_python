# orchestration-service 엔터티 설명

## 목적

- `orchestration-service`가 소유하는 saga 상태 저장소 구조를 정의한다.
- 외부 멱등성과 내부 사가 상태가 어느 DB에 저장되는지 명확히 한다.

## 엔터티 개요

- `SAGA_OPERATION`: 입차/출차 saga의 진행 상태, 멱등성, 결과 snapshot을 저장한다.

## SAGA_OPERATION

`orchestration_db`의 authoritative saga 상태 테이블이다.  
외부 `Idempotency-Key`와 내부 `operation_id`를 함께 관리한다.

| 컬럼명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `operation_id` | `varchar(64)` | Y | saga 식별자 PK |
| `idempotency_key` | `varchar(128)` | Y | 외부 요청 멱등성 키 |
| `saga_type` | `varchar(16)` | Y | `ENTRY` 또는 `EXIT` |
| `status` | `varchar(32)` | Y | 현재 saga 상태 |
| `current_step` | `varchar(64)` | N | 현재 진행 단계 |
| `history_id` | `bigint` | N | 생성/종료된 주차 이력 식별자 |
| `vehicle_num` | `varchar(20)` | N | 대상 차량 번호 |
| `slot_id` | `bigint` | N | 대상 slot 식별자 |
| `last_error_code` | `varchar(64)` | N | 마지막 실패 코드 |
| `last_error_message` | `text` | N | 마지막 실패 메시지 |
| `result_snapshot` | `json` | Y | 외부 응답 재사용용 결과 snapshot |
| `completed_compensations` | `json` | Y | 완료된 보상 단계 목록 |
| `created_at` | `timestamp` | Y | 생성 시각 |
| `updated_at` | `timestamp` | Y | 최종 갱신 시각 |
| `completed_at` | `timestamp` | N | 완료/실패 확정 시각 |

제약/인덱스:
- PK: `operation_id`
- 유니크 제약: `idempotency_key`

운영 규칙:
- 같은 `idempotency_key` 재요청은 기존 `result_snapshot`을 재사용한다.
- 보상 완료 시 `completed_compensations`에 실행된 보상 step을 기록한다.
- 다른 서비스는 이 테이블을 직접 읽지 않고, 오케스트레이션 API를 통해 상태를 조회한다.
