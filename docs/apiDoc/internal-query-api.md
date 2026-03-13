# 내부 parking-query API

이 문서는 `orchestration-service`가 호출하는 `parking-query-service` 내부 HTTP API를 정리합니다.

특징:
- 조회 1개 + projection 반영용 `POST` API들로 구성됩니다.
- projection 반영용 `POST` API는 서비스 간 호출을 위해 `csrf_exempt` 처리되어 있습니다.

관련 URL 등록:
- services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/urls.py

## 1. 현재 주차 projection 조회 기능

- Method: `GET`
- URL: `/internal/parking-query/current-parking/{vehicle_num}`

성공 응답 예시:

```json
{
  "vehicle_num": "69가-3455",
  "slot_id": 11,
  "zone_id": 1,
  "slot_type": "GENERAL",
  "entry_at": "2026-03-12T09:00:00+09:00"
}
```

실패 응답 시에는 (`404`) 에러 반환:
- `404`: projection 없음

관련 코드:
- 내부 HTTP 뷰: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/views.py`
- 내부 projection 유스케이스: `services/parking-query-service/src/parking_query_service/parking_view/application/use_cases/internal_projection.py`
- 계약 테스트: `services/parking-query-service/test/contract/test_ct_internal_projection_view_success.py`

## 2. 입차 projection 반영 기능

- Method: `POST`
- URL: `/internal/parking-query/entries`

요청 본문:
- `operation_id`
- `vehicle_num`
- `slot_id`
- `zone_id`
- `slot_type`
- `entry_at`

성공 응답 예시:

```json
{
  "projected": true
}
```

실패 응답 시에는 (`404`, `409`) 에러 반환 가능

관련 코드:
- 내부 HTTP 뷰: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/views.py`
- 내부 projection 유스케이스: `services/parking-query-service/src/parking_query_service/parking_view/application/use_cases/internal_projection.py`
- 계약 테스트: `services/parking-query-service/test/contract/test_ct_internal_projection_view_success.py`

## 3. 입차 projection 보상 기능

- Method: `POST`
- URL: `/internal/parking-query/entries/compensations`

요청 본문:
- `operation_id`
- `vehicle_num`

성공 응답 예시:

```json
{
  "reverted": true
}
```

관련 코드:
- 내부 HTTP 뷰: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/views.py`
- 내부 projection 유스케이스: `services/parking-query-service/src/parking_query_service/parking_view/application/use_cases/internal_projection.py`
- 계약 테스트: `services/parking-query-service/test/contract/test_ct_internal_projection_view_success.py`

## 4. 출차 projection 반영 기능

- Method: `POST`
- URL: `/internal/parking-query/exits`

요청 본문:
- `operation_id`
- `vehicle_num`

성공 응답 예시:

```json
{
  "projected": true
}
```

실패 응답 시에는 (`404`, `409`) 에러 반환 가능

관련 코드:
- 내부 HTTP 뷰: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/views.py`
- 내부 projection 유스케이스: `services/parking-query-service/src/parking_query_service/parking_view/application/use_cases/internal_projection.py`
- 계약 테스트: `services/parking-query-service/test/contract/test_ct_internal_projection_view_success.py`

## 5. 출차 projection 보상 기능

- Method: `POST`
- URL: `/internal/parking-query/exits/compensations`

요청 본문:
- `operation_id`
- `vehicle_num`
- `slot_id`
- `zone_id`
- `slot_type`
- `entry_at`

성공 응답 예시:

```json
{
  "restored": true
}
```

관련 코드:
- 내부 HTTP 뷰: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/views.py`
- 내부 projection 유스케이스: `services/parking-query-service/src/parking_query_service/parking_view/application/use_cases/internal_projection.py`
- 계약 테스트: `services/parking-query-service/test/contract/test_ct_internal_projection_view_success.py`
