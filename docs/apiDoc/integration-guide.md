# 프론트/팀 연동 가이드

프로젝트 API를 연동 방법 정리

## 1. 프론트엔드

프론트엔드는 공개 API만 기준으로 연동

- `public-query-api.md`
- `gateway-api.md`

내부 서비스 간 통신용이라 연동 대상 제외
- `/internal/*`

## 2. 입차/출차 봇 API 연동

입차/출차는 `gateway API`를 기준으로 연동

사용 경로:
- 입차: `POST /api/v1/parking/entries`
- 출차: `POST /api/v1/parking/exits`
- 상태 조회: `GET /api/v1/saga-operations/{operation_id}`

프론트는 `parking-command-service` 직접 호출이 아닌,
`orchestration-service`가 제공하는 게이트웨이 API를 통해 입차/출차를 요청

이유:
- 차량 검증
- Zone 정책 검증
- parking-command 처리
- parking-query 반영
- 실패 시 보상 처리

위 흐름이 오케스트레이션 단에서 하나로 묶여 있기 때문입니다.

관련 코드:
- `services/orchestration-service/src/orchestration_service/saga/interfaces/http/urls.py`
- `services/orchestration-service/src/orchestration_service/saga/application/use_cases/entry_saga.py`
- `services/orchestration-service/src/orchestration_service/saga/application/use_cases/exit_saga.py`

## 3. 조회 기능

조회 기능은 `public-query API`를 기준으로 연동

사용 경로:
- 전체 여석 조회: `GET /api/zones/availabilities`
- Zone별 슬롯 목록 조회: `GET /zones/{zone_id}/slots`
- 차량 현재 위치 조회: `GET /api/parking/current/{vehicle_num}`

 
조회 `GET` API는 공개 API 기준으로 바로 연동 가능합니다.


## 4. 백엔드 서비스 간 연동

백엔드 서비스 간 연동은 내부 API 또는 gRPC를 사용합니다.

예:
- `orchestration-service` -> `parking-command-service`
- `orchestration-service` -> `parking-query-service`
- `orchestration-service` -> `vehicle-service`
- `orchestration-service` -> `zone-service`

