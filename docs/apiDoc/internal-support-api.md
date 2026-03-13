# 내부 지원 API

이 문서는 다른 서비스가 호출하는 내부 조회성 API를 정리합니다.

관련 URL 등록:
- services/vehicle-service/src/vehicle_service/vehicle/interfaces/http/urls.py
- services/zone-service/src/zone_service/zone_catalog/interfaces/http/urls.py

## 1. 차량 조회 기능

- Method: `GET`
- URL: `/internal/vehicles/{vehicle_num}`

설명:
- 차량 존재 여부와 차량 타입을 확인할 때 사용합니다.

성공 응답 예시:

```json
{
  "vehicle_num": "12가3456",
  "vehicle_type": "GENERAL"
}
```

실패 응답 시에는 (`404`) 에러 반환:
- `404`: 차량 없음

관련 코드:
- URL: `services/vehicle-service/src/vehicle_service/vehicle/interfaces/http/urls.py`
- 뷰: `services/vehicle-service/src/vehicle_service/vehicle/interfaces/http/views.py`
- 유스케이스: `services/vehicle-service/src/vehicle_service/vehicle/application/use_cases/get_vehicle.py`

## 2. 슬롯 입차 정책 조회 기능

- Method: `GET`
- URL: `/internal/zones/slots/{slot_id}/entry-policy`

설명:
- 특정 슬롯의 Zone, 슬롯 타입, 입차 허용 여부를 조회합니다.
- 오케스트레이션/parking-command에서 입차 가능 여부 판단에 사용합니다.

성공 응답 예시:

```json
{
  "slot_id": 7,
  "zone_id": 1,
  "slot_type": "GENERAL",
  "zone_active": true,
  "entry_allowed": true
}
```

실패 응답 시에는 (`404`) 에러 반환:
- `404`: 슬롯 없음

관련 코드:
- URL: `services/zone-service/src/zone_service/zone_catalog/interfaces/http/urls.py`
- 뷰: `services/zone-service/src/zone_service/zone_catalog/interfaces/http/views.py`
- 도메인 정책: `services/zone-service/src/zone_service/zone_catalog/domain/policies/entry_policy.py`
- 계약 확인: `services/orchestration-service/test/contract/test_ct_or_dependency_clients.py`
