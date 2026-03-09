# 입출차 기록 API 후속 작업 수행 명세서

## 1. 대상

- 기능: `parking-command-service` 입출차 기록 API 후속 보강
- 기준 문서:
  - [TEST_SPEC_PARKING_RECORD_API.md](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/test/TEST_SPEC_PARKING_RECORD_API.md)
  - [TEST_EXECUTION_PARKING_RECORD_API.md](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/test/TEST_EXECUTION_PARKING_RECORD_API.md)
- 실행 환경: `./.venv/bin/python manage.py test --settings=park_py.settings_test`

## 2. 페이즈별 진행 기록

### 2.1 Phase 1. 주차 이력 재사용 방지

- 커밋: `e157770` (`test: prevent parking history reuse across occupancies`)
- 변경 요약:
  - `SlotOccupancy.history`를 `OneToOneField`로 강화
  - 동일 `ParkingHistory`를 여러 점유가 공유하지 못하도록 DB 제약 추가
  - repository 테스트에 중복 참조 실패 케이스 추가
- 실행 명령:

```bash
./.venv/bin/python manage.py test services/parking-command-service/test/repository --settings=park_py.settings_test
```

- 결과: `6 tests / OK`

### 2.2 Phase 2. command 의존성 조립 분리

- 커밋: `1e90263` (`refactor: extract parking record dependencies`)
- 변경 요약:
  - view에서 service/repository 직접 생성 책임 제거
  - `dependencies.py`에서 command service 조립 일원화
  - 조립 결과 단위 테스트 추가
- 실행 명령:

```bash
./.venv/bin/python manage.py test services/parking-command-service/test/unit --settings=park_py.settings_test
```

- 결과: `9 tests / OK`

### 2.3 Phase 3. serializer edge case 계약 보강

- 커밋: `55808d0` (`test: cover parking record serializer edge cases`)
- 변경 요약:
  - malformed JSON
  - JSON object 외 body
  - `slot_id` 비정수 타입
  - 위 3건에 대한 `400 bad_request` 계약 추가
- 실행 명령:

```bash
./.venv/bin/python manage.py test services/parking-command-service/test/contract --settings=park_py.settings_test
```

- 결과: `10 tests / OK`

### 2.4 Phase 4. query projection 연결

- 커밋: `e2bd77f` (`feat: connect parking record query projections`)
- 변경 요약:
  - command service에 projection writer 주입
  - 입차 시 `CurrentParkingView` 생성/갱신
  - 출차 시 `CurrentParkingView` 제거
  - `ZoneAvailability` 재계산 반영
  - 오래된 history가 늦게 들어와도 최신 projection을 덮어쓰지 않는 회귀 테스트 추가
  - SQLite 테스트 환경 write lock을 위한 제한적 재시도 추가
- 실행 명령:

```bash
./.venv/bin/python manage.py test services/parking-command-service/test/acceptance --settings=park_py.settings_test
./.venv/bin/python manage.py test services/parking-command-service/test/repository --settings=park_py.settings_test
./.venv/bin/python manage.py test services/parking-command-service/test/unit services/parking-command-service/test/contract --settings=park_py.settings_test
```

- 결과:
  - `14 acceptance tests / OK`
  - `9 repository tests / OK`
  - `21 unit+contract tests / OK`

## 3. 최종 통합 실행 기록

- 실행 명령:

```bash
./.venv/bin/python manage.py test \
  services/parking-command-service/test/acceptance \
  services/parking-command-service/test/contract \
  services/parking-command-service/test/unit \
  services/parking-command-service/test/repository \
  --settings=park_py.settings_test
```

- 결과: `44 tests / OK`

## 4. 이번 후속 작업에서 추가된 주요 파일

- `services/parking-command-service/src/parking_command_service/repositories/query_projection_repository.py`
- `services/parking-command-service/test/acceptance/test_parking_record_projection_api.py`
- `services/parking-command-service/test/repository/test_parking_record_projection_repository.py`

## 5. 최종 상태

- command API의 write 모델 정합성 검증은 유지된다.
- serializer edge case 계약이 보강되었다.
- command 완료 시 query projection이 동기화된다.
- `CurrentParkingView`, `ZoneAvailability`에 대한 회귀 테스트가 추가되었다.
- 현재 parking-command-service 테스트 스위트는 `44 tests / OK` 상태다.
