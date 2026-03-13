# 내부 parking-command API

이 문서는 `orchestration-service`가 호출하는 `parking-command-service` 내부 HTTP API를 정리합니다.

특징:
- 모두 `POST`
- 서비스 간 호출을 위해 `csrf_exempt` 처리되어 있습니다.

관련 URL 등록:
- services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/urls.py

## 1. 내부 입차 기능

- Method: `POST`
- URL: `/internal/parking-command/entries`

요청 본문:
- `operation_id`
- `vehicle_num`
- `slot_id`
- `requested_at`

성공 응답 예시 (`201`):

```json
{
  "history_id": 101,
  "slot_id": 7,
  "vehicle_num": "12가3456",
  "entry_at": "2026-03-10T10:00:00+09:00",
  "status": "PARKED"
}
```

실패 응답 시에는 (`404`, `409`) 에러 반환 가능

관련 코드:
- 내부 HTTP 뷰: `services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/internal_views.py`
- 내부 use case: `services/parking-command-service/src/parking_command_service/parking_record/application/use_cases/internal_commands.py`
- 오케스트레이션 클라이언트: `services/orchestration-service/src/orchestration_service/clients/parking_command.py`

## 2. 내부 입차 보상 기능

- Method: `POST`
- URL: `/internal/parking-command/entries/compensations`

요청 본문:
- `operation_id`
- `history_id`

성공 응답 예시 (`200`):

```json
{
  "history_id": 101,
  "slot_released": true
}
```

관련 코드:
- 내부 HTTP 뷰: `services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/internal_views.py`
- 내부 use case: `services/parking-command-service/src/parking_command_service/parking_record/application/use_cases/internal_commands.py`

## 3. 내부 출차 기능

- Method: `POST`
- URL: `/internal/parking-command/exits`

요청 본문:
- `operation_id`
- `vehicle_num`
- `requested_at`

성공 응답 예시 (`200`):

```json
{
  "history_id": 101,
  "slot_id": 7,
  "vehicle_num": "12가3456",
  "exit_at": "2026-03-10T12:00:00+09:00",
  "status": "EXITED"
}
```

실패 응답 시에는 (`404`, `409`) 에러 반환 가능

관련 코드:
- 내부 HTTP 뷰: `services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/internal_views.py`
- 내부 use case: `services/parking-command-service/src/parking_command_service/parking_record/application/use_cases/internal_commands.py`
- 오케스트레이션 클라이언트: `services/orchestration-service/src/orchestration_service/clients/parking_command.py`

## 4. 내부 출차 보상 기능

- Method: `POST`
- URL: `/internal/parking-command/exits/compensations`

요청 본문:
- `operation_id`
- `history_id`

성공 응답 예시 (`200`):

```json
{
  "history_id": 101,
  "slot_reoccupied": true
}
```

관련 코드:
- 내부 HTTP 뷰: `services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/internal_views.py`
- 내부 use case: `services/parking-command-service/src/parking_command_service/parking_record/application/use_cases/internal_commands.py`
- 오케스트레이션 클라이언트: `services/orchestration-service/src/orchestration_service/clients/parking_command.py`
