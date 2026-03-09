# 입출차 기록 API 테스트 수행 명세서

## 1. 대상

- 기능: `parking-command-service` 입출차 기록 API
- 기준 명세: [TEST_SPEC_PARKING_RECORD_API.md](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/test/TEST_SPEC_PARKING_RECORD_API.md)
- 실행 환경: `./.venv/bin/python manage.py test --settings=park_py.settings_test`

## 2. 페이즈별 진행 기록

### 2.1 Acceptance (AT)

- 커밋: `d6c524b` (`feat: add parking record acceptance flow`)
- 실행 명령:

```bash
./.venv/bin/python manage.py test services/parking-command-service/test/acceptance --settings=park_py.settings_test
```

- 결과: `10 tests / OK`
- 검증 범위:
  - 입차 성공 시 활성 세션 및 점유 생성
  - 출차 성공 시 세션 종료 및 점유 해제
  - 차량 미등록 / 슬롯 미존재 / 슬롯 비활성 / 슬롯 점유 중 / 활성 세션 중복 거부
  - 잘못된 payload, naive datetime, 시간 역전 거부
  - 동시 입차 경쟁 시 `1건 성공 / 1건 충돌`

### 2.2 Contract (CT)

- 커밋: `805db64` (`test: add parking record contract coverage`)
- 실행 명령:

```bash
./.venv/bin/python manage.py test services/parking-command-service/test/contract --settings=park_py.settings_test
```

- 결과: `7 tests / OK`
- 검증 범위:
  - 입차/출차 성공 응답 스키마
  - command 응답에 write 필드만 노출되는지 확인
  - `400 / 404 / 409` 표준 오류 응답 계약
  - 시간 역전 오류 계약

### 2.3 Unit (UT)

- 커밋: `9c89b58` (`test: add parking record unit coverage`)
- 실행 명령:

```bash
./.venv/bin/python manage.py test services/parking-command-service/test/unit --settings=park_py.settings_test
```

- 결과: `8 tests / OK`
- 검증 범위:
  - 차량 번호 정규화
  - `ParkingHistory.start()` / `exit()` 상태 전이
  - `SlotOccupancy.occupy()` / `release()` 상태 전이
  - serializer의 timezone-aware 검증
  - command service의 write-only 응답 조합

### 2.4 Repository/DB (RT)

- 커밋: `46492a9` (`test: add parking record repository coverage`)
- 실행 명령:

```bash
./.venv/bin/python manage.py test services/parking-command-service/test/repository --settings=park_py.settings_test
```

- 결과: `5 tests / OK`
- 검증 범위:
  - 동일 차량 활성 세션 유니크
  - 동일 슬롯 활성 세션 유니크
  - 점유 상태 체크 제약
  - 슬롯별 점유 단건성
  - 동시 입차 경쟁 시 DB 최종 상태 일관성

## 3. 전체 통합 실행 기록

- 실행 명령:

```bash
./.venv/bin/python manage.py test \
  services/parking-command-service/test/acceptance \
  services/parking-command-service/test/contract \
  services/parking-command-service/test/unit \
  services/parking-command-service/test/repository \
  --settings=park_py.settings_test
```

- 결과: `30 tests / OK`

## 4. 생성된 테스트 파일

- `services/parking-command-service/test/acceptance/test_parking_record_api.py`
- `services/parking-command-service/test/contract/test_parking_record_api_contract.py`
- `services/parking-command-service/test/unit/test_parking_record_domain.py`
- `services/parking-command-service/test/unit/test_parking_record_serializers.py`
- `services/parking-command-service/test/unit/test_parking_record_service.py`
- `services/parking-command-service/test/repository/test_parking_record_repository.py`
- `services/parking-command-service/test/support/factories.py`

## 5. 메모

- CQRS 기준에 따라 이번 테스트는 `parking-command-service`의 write 책임만 검증한다.
- query projection 반영과 read-after-write 보장은 이번 문서 범위에 포함하지 않는다.
