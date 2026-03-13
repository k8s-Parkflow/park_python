# 조회 API

조회용 API 정리

관련 URL 등록:
- park_py/urls.py
- services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/urls.py

## 1. 전체 Zone 여석 조회 기능

- Method: `GET`
- URL: `/api/zones/availabilities`
- Query Parameter:
  - `slot_type` (선택): `GENERAL`, `EV`, `DISABLED`

설명:
- `slot_type`를 넘기면 해당 타입의 전체 Zone 여석 합계를 반환합니다.
- `slot_type`를 생략하면 지원 타입 전체의 합계를 반환합니다.
- 한 번의 호출로 타입별 3개 값을 모두 나눠서 반환하는 API는 현재 없습니다.

호출 예시:

```http
GET /api/zones/availabilities?slot_type=GENERAL
```

성공 응답 예시:

```json
{
  "slotType": "GENERAL",
  "availableCount": 12
}
```

전체 합계 조회 예시:

```http
GET /api/zones/availabilities
```

```json
{
  "availableCount": 78
}
```

실패 응답 시에는 (`400`) 에러 반환:

```json
{
  "error": {
    "code": "bad_request",
    "message": "잘못된 요청입니다.",
    "details": {
      "slot_type": ["지원하지 않는 슬롯 타입입니다."]
    }
  }
}
```

관련 코드:
- 뷰: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/views.py`
- 서비스: `services/parking-query-service/src/parking_query_service/parking_view/application/use_cases/get_zone_availability.py`
- 저장소: `services/parking-query-service/src/parking_query_service/parking_view/infrastructure/persistence/repositories/zone_availability_repository.py`
- 계약 테스트: `services/parking-query-service/test/contract/test_ct_typed_availability.py`

## 2. Zone별 슬롯 목록 조회 기능

- Method: `GET`
- URL: `/zones/{zone_id}/slots`

설명:
- 특정 Zone의 슬롯 목록을 반환합니다.
- 각 슬롯의 타입(`category`), 활성 여부(`isActive`), 현재 점유 차량(`vehicleNum`)이 포함됩니다.
- 프론트가 이 목록을 기준으로 Zone별 여석 수를 계산할 수 있습니다.
- 서버는 이 API에서 Zone별 합계 카운트를 별도 필드로 내려주지 않습니다.

호출 예시:

```http
GET /zones/1/slots
```

성공 응답 예시:

```json
{
  "zoneId": 1,
  "slots": [
    {
      "slotId": 11,
      "slot_name": "A001",
      "category": "GENERAL",
      "isActive": true,
      "vehicleNum": "69가-3455"
    },
    {
      "slotId": 12,
      "slot_name": "A002",
      "category": "EV",
      "isActive": false,
      "vehicleNum": null
    }
  ]
}
```

실패 응답 시에는 (`404`) 에러 반환:

```json
{
  "error": {
    "code": "not_found",
    "message": "존을 찾을 수 없습니다."
  }
}
```

관련 코드:
- 뷰: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/views.py`
- URL: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/urls.py`
- 서비스: `services/parking-query-service/src/parking_query_service/services/zone_slot_query_service.py`
- 저장소: `services/parking-query-service/src/parking_query_service/repositories/zone_slot_repository.py`
- 수용 테스트: `services/parking-query-service/test/acceptance/test_at_zone_slot_list.py`

## 3. 차량 현재 위치 조회 기능

- Method: `GET`
- URL: `/api/parking/current/{vehicle_num}`

설명:
- 차량 번호 기준 현재 주차 위치를 조회합니다.
- 사용자 GPS 위치가 아니라, 현재 주차 projection 기준 `zone_name`, `slot_name`을 반환합니다.

호출 예시:

```http
GET /api/parking/current/69가-3455
```

성공 응답 예시:

```json
{
  "vehicle_num": "69가-3455",
  "zone_name": "A존",
  "slot_name": "A033"
}
```

대표 실패 응답:
- 잘못된 차량 번호 형식: `400`
- 차량 자체가 없음: `404`
- 차량은 있지만 현재 주차 중이 아님: `404`

관련 코드:
- 뷰: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/views.py`
- 서비스: `services/parking-query-service/src/parking_query_service/parking_view/application/use_cases/get_current_location.py`
- 입력 검증: `services/parking-query-service/src/parking_query_service/parking_view/interfaces/http/forms.py`
- 성공 테스트: `services/parking-query-service/test/acceptance/test_at_pq_loc_current_location_success.py`
- 오류 테스트: `services/parking-query-service/test/contract/test_ct_pq_loc_current_location_errors.py`
