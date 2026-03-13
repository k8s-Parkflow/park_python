# 오케스트레이션 게이트웨이 API

이 문서는 `orchestration-service`가 제공하는 사가 기반 공개 API 정리

관련 URL 등록:
- orchestration_service/saga/interfaces/http/urls.py
- 
## 공통 주의사항

- `POST` 호출 시 `Idempotency-Key` 헤더 필요
- 공개 `POST` API이므로 브라우저에서 직접 테스트할 때는 CSRF 보호를 받음.
- Swagger(`/api/docs/swagger`) 기반 테스트 지원

## 1. 입차 기능

- Method: `POST`
- URL: `/api/v1/parking/entries`
- Header:
  - `Idempotency-Key`: 필수

요청 본문:
- `vehicle_num`
- `slot_id`
- `requested_at`

요청 예시:

```json
{
  "vehicle_num": "12가3456",
  "slot_id": 7,
  "requested_at": "2026-03-10T10:00:00+09:00"
}
```

성공 응답 예시 (`201`):

```json
{
  "operation_id": "entry-op-001",
  "status": "COMPLETED",
  "history_id": 101,
  "vehicle_num": "12가3456",
  "slot_id": 7,
  "entry_at": "2026-03-10T10:00:00+09:00"
}
```

실패 응답 시에는 (`409` 또는 `500`) 에러 반환:

```json
{
  "error": {
    "code": "conflict",
    "message": "출차 SAGA 처리 중 보상 트랜잭션이 실행되었습니다.",
    "details": {
      "operation_id": "exit-op-001",
      "status": "COMPENSATED",
      "failed_step": "UPDATE_QUERY_EXIT"
    }
  }
}
```

관련 코드:
- 뷰: `orchestration_service/saga/interfaces/http/views.py`
- 계약 테스트: `park_py/tests/orchestration_service/contract/test_ct_or_gateway_api.py`
- 실제 HTTP 수용 테스트: `test/acceptance/test_at_or_real_saga_http.py`

## 2. 출차 기능

- Method: `POST`
- URL: `/api/v1/parking/exits`
- Header:
  - `Idempotency-Key`: 필수

요청 본문:
- `vehicle_num`
- `requested_at`

요청 예시:

```json
{
  "vehicle_num": "12가3456",
  "requested_at": "2026-03-10T12:00:00+09:00"
}
```

성공 응답 예시 (`200`):

```json
{
  "operation_id": "exit-op-001",
  "status": "COMPLETED",
  "history_id": 101,
  "vehicle_num": "12가3456",
  "slot_id": 7,
  "exit_at": "2026-03-10T12:00:00+09:00"
}
```

실패 시 응답 구조는 입차와 동일하게 `error.details.operation_id`, `status`, `failed_step`를 포함

관련 코드:
- 뷰: `orchestration_service/saga/interfaces/http/views.py`
- 계약 테스트: `park_py/tests/orchestration_service/contract/test_ct_or_gateway_api.py`
- 실제 HTTP 수용 테스트: `services/orchestration-service/test/acceptance/test_at_or_real_saga_http.py`

## 3. 사가 상태 조회

- Method: `GET`
- URL: `/api/v1/saga-operations/{operation_id}`

성공 응답 예시:

```json
{
  "operation_id": "entry-op-001",
  "saga_type": "ENTRY",
  "status": "FAILED",
  "current_step": "UPDATE_QUERY_ENTRY",
  "history_id": 101,
  "vehicle_num": "12가3456",
  "slot_id": 7,
  "last_error_code": "projection_update_failed",
  "last_error_message": "parking-query-service timeout"
}
```

관련 코드:
- 뷰: `orchestration_service/saga/interfaces/http/views.py`
- 계약 테스트: `park_py/tests/orchestration_service/contract/test_ct_or_gateway_api.py`
