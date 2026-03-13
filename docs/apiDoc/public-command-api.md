# 주차 command API

입차/출차 API를 정리

관련 URL 등록:
- services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/urls.py

## 공통 주의사항

- 브라우저에서 직접 `POST` 테스트 시 CSRF 보호를 받음.
- Swagger(`/api/docs/swagger`) 기반 테스트 지원

## 1. 입차 기능

- Method: `POST`
- URL: `/api/parking/entry`
- Content-Type: `application/json`

요청 필드:
- `vehicle_num`: 차량 번호, 문자열
- `zone_id`: 구역 ID, 정수
- `slot_name`: 슬롯 코드, 문자열, 대문자 형식
- `slot_id`: 슬롯 ID, 정수
- `entry_at`: 선택, timezone-aware ISO 8601 문자열

요청 예시:

```json
{
  "vehicle_num": "69가-3455",
  "zone_id": 1,
  "slot_name": "A001",
  "slot_id": 11,
  "entry_at": "2026-03-10T10:00:00+09:00"
}
```

성공 응답 예시 (`201`):

```json
{
  "history_id": 101,
  "vehicle_num": "69가-3455",
  "zone_id": 1,
  "slot_code": "A001",
  "slot_name": "A001",
  "slot_id": 11,
  "status": "PARKED",
  "entry_at": "2026-03-10T10:00:00+09:00",
  "exit_at": null
}
```

실패 응답 시에는 (`400`, `404`, `409`) 에러 반환:
- `400`: 필수값 누락, 차량 번호 형식 오류, datetime 형식 오류
- `404`: 차량 또는 슬롯을 찾을 수 없음
- `409`: 비활성 슬롯, 점유 중 슬롯, 이미 주차 중인 차량 등 충돌

관련 코드:
- 뷰: `services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/views.py`
- 요청 파서: `services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/serializers.py`
- 응용 서비스 DTO: `services/parking-command-service/src/parking_command_service/parking_record/application/dtos.py`
- 수용 테스트: `services/parking-command-service/test/acceptance/test_parking_record_api.py`

## 2. 출차 기능

- Method: `POST`
- URL: `/api/parking/exit`
- Content-Type: `application/json`

요청 필드:
- `vehicle_num`: 차량 번호, 문자열
- `zone_id`: 구역 ID, 정수
- `slot_name`: 슬롯 코드, 문자열
- `slot_id`: 슬롯 ID, 정수
- `exit_at`: 선택, timezone-aware ISO 8601 문자열

요청 예시:

```json
{
  "vehicle_num": "69가-3455",
  "zone_id": 1,
  "slot_name": "A001",
  "slot_id": 11,
  "exit_at": "2026-03-10T12:00:00+09:00"
}
```

성공 응답 예시 (`200`):

```json
{
  "history_id": 101,
  "vehicle_num": "69가-3455",
  "zone_id": 1,
  "slot_code": "A001",
  "slot_name": "A001",
  "slot_id": 11,
  "status": "EXITED",
  "entry_at": "2026-03-10T10:00:00+09:00",
  "exit_at": "2026-03-10T12:00:00+09:00"
}
```

실패 응답 시에는 (`400`, `404`, `409`) 에러 반환:
- `400`: 형식 오류, 출차 시각 역전
- `404`: 활성 주차 이력이 없음
- `409`: 위치 충돌 등 도메인 충돌

관련 코드:
- 뷰: `services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/views.py`
- 요청 파서: `services/parking-command-service/src/parking_command_service/parking_record/interfaces/http/serializers.py`
- 수용 테스트: `services/parking-command-service/test/acceptance/test_parking_record_api.py`
