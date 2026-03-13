# 프론트/팀 연동 가이드

API 연동 정리 문서

## 1. 프론트엔드는 무엇을 보면 되는가

프론트엔드는 공개 API만 기준으로 연동

프론트가 참고해야 하는 문서:
- `public-query-api.md`
- `gateway-api.md`

프론트가 직접 호출하면 안 되는 경로:
- `/internal/*`

내부 경로는 서비스 간 통신용

## 2. 입차/출차는 어떤 API로 연동해야 하는가

입차/출차는 `gateway API`를 기준으로 연동

사용 경로:
- 입차: `POST /api/v1/parking/entries`
- 출차: `POST /api/v1/parking/exits`
- 상태 조회: `GET /api/v1/saga-operations/{operation_id}`

`parking-command-service`를 직접 호출하는 방식이 아니라,
`orchestration-service`가 제공하는 게이트웨이 API를 통해 입차/출차를 요청

이유:
- 차량 검증
- Zone 정책 검증
- parking-command 처리
- parking-query 반영
- 실패 시 보상 처리

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

조회 `GET` API는 공개 API 기준으로 바로 연동 가능

## 4. 연동 시 주의할 점

조회 API는 공개 API 기준으로 바로 연동 가능

다만 입차/출차 `POST` API는 현재 Django CSRF 보호가 활성화되어 있어,
브라우저 기반 프론트엔드가 별도 처리 없이 바로 호출하기는 어려운 상태

즉, 현재 상태를 정리하면:
- 조회 API 연동: 가능
- 입차/출차 API 연동: 공개 API 기준으로 붙어야 하지만 CSRF 처리 고려 필요

관련 코드:
- `park_py/settings.py`
- `park_py/openapi.py`
- `services/orchestration-service/src/orchestration_service/settings.py`

## 5. 백엔드 서비스 간 연동은 어떻게 진행되는가

백엔드 서비스 간 연동은 내부 API 또는 gRPC를 사용합니다.

예:
- `orchestration-service` -> `parking-command-service`
- `orchestration-service` -> `parking-query-service`
- `orchestration-service` -> `vehicle-service`
- `orchestration-service` -> `zone-service`

이 경로들은 프론트 연동 대상이 아닙니다.

## 6. 내부 통신은 자동으로 되는가

현재 프로젝트 기준으로는 `완전 자동`이 아니라 `반자동`

- 프론트가 gateway API를 호출하면, 그 다음 내부 통신은 자동으로 진행됩니다.
- 하지만 그 자동 통신이 가능하도록 서비스 실행 환경은 백엔드에서 직접 맞춰야 합니다.

즉, 기존에 구현된 입차/출차 흐름은 자동으로 이어지지만,
실행 환경을 구성하는 일은 자동으로 생기지 않습니다.

## 7. 현재 입차/출차 흐름은 어떻게 진행되는가

프론트가 아래 공개 API를 호출하면:
- `POST /api/v1/parking/entries`
- `POST /api/v1/parking/exits`

그 다음 내부에서는 `orchestration-service`가 순서대로 다음 작업을 수행합니다.

입차 시:
- `vehicle-service`로 차량 검증
- `zone-service`로 슬롯/입차 정책 검증
- `parking-command-service`로 입차 처리
- `parking-query-service`로 조회 projection 반영
- 중간 실패 시 보상 처리

출차 시:
- `parking-command-service`에서 현재 활성 주차 조회
- `parking-command-service`로 출차 처리
- `parking-query-service`로 조회 projection 반영
- 중간 실패 시 보상 처리

즉, 프론트가 내부 API를 각각 호출하는 구조가 아니라,
게이트웨이 한 번 호출하면 오케스트레이션이 내부 서비스를 자동 호출하는 구조입니다.

관련 코드:
- `services/orchestration-service/src/orchestration_service/saga/application/use_cases/entry_saga.py`
- `services/orchestration-service/src/orchestration_service/saga/application/use_cases/exit_saga.py`

## 8. 내부 통신 환경 구성 문서

배포 이후 서비스 통신 연결 방법과 gRPC 재구성 방법은 아래 문서를 참고

- `docs/architecture/gRPC 통신 연결법.md`

## 9. 결론

팀원들이 연동할 때 기준은 아래처럼 가져가면 됩니다.

- 프론트: 공개 API만 사용
- 조회: `public-query-api.md`
- 입차/출차: `gateway-api.md`
- 내부 서비스 연동: `internal-*.md` 참고

한 줄로 정리하면,
프론트는 조회와 입차/출차 모두 공개 API로 붙되, 입차/출차는 `gateway API`를 사용해야 합니다.
그리고 게이트웨이 호출 이후 내부 서비스 간 통신은 자동으로 진행되지만,
그 자동 통신이 가능하도록 서비스 실행 환경은 백엔드에서 직접 준비해야 합니다.
