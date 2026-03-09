# parking-command-service 패키지/클래스 구현 설명

## 목적

- `parking_command_service`의 패키지별 책임과 클래스별 담당 기능을 한 문서에서 확인할 수 있도록 정리한다.
- 현재 코드 기준의 구현 방식을 계층별로 설명해, 이후 수정 시 책임 경계가 흐려지지 않도록 한다.

## 전체 구조

`parking_command_service`는 CQRS 기준에서 write 모델을 담당하는 Django 앱이다.

주요 흐름:
1. `urls.py`가 입차/출차 HTTP 엔드포인트를 노출한다.
2. `views/parking_record_views.py`가 요청 바디를 command 객체로 변환한다.
3. `serializers/parking_record_serializers.py`가 JSON 파싱과 입력 검증을 수행한다.
4. `services/parking_record_service.py`가 트랜잭션 안에서 입차/출차 유스케이스를 실행한다.
5. `repositories/*`가 DB 접근과 query projection 동기화를 담당한다.
6. `models/*`가 도메인 상태와 불변식을 보장한다.

## 패키지별 책임

### 루트 패키지

- [apps.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/apps.py)
  - `ParkingCommandServiceConfig`를 통해 Django 앱 등록 정보를 제공한다.
- [urls.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/urls.py)
  - 입차/출차 API 라우팅만 담당한다.
- [dependencies.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/dependencies.py)
  - command service를 실제 repository 구현체와 projection writer로 조립한다.
- [dtos.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/dtos.py)
  - 계층 간에 전달되는 command/snapshot 데이터 구조를 정의한다.
- [exceptions.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/exceptions.py)
  - 도메인/애플리케이션 오류를 HTTP 오류 코드와 연결한다.
- [vehicle_nums.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/vehicle_nums.py)
  - 차량 번호 정규화와 형식 검증을 공통 유틸리티로 제공한다.

### `views`

- HTTP 요청과 응답 변환만 담당한다.
- 비즈니스 로직이나 ORM 직접 호출은 두지 않고 service에 위임한다.

### `serializers`

- JSON 본문 파싱, 필수값 검증, 타입 검증, datetime 검증을 담당한다.
- 검증이 끝난 뒤에는 service가 바로 사용할 수 있는 command DTO를 반환한다.

### `services`

- 입차/출차 유스케이스의 애플리케이션 계층이다.
- `transaction.atomic()` 경계를 두고 repository와 도메인 모델을 조합한다.
- write가 성공한 뒤 query projection 동기화 호출도 여기서 오케스트레이션한다.

### `models`

- `ParkingSlot`, `ParkingHistory`, `SlotOccupancy`가 핵심 write 모델이다.
- 상태 전이 규칙과 데이터 일관성 검증을 모델 메서드와 DB 제약으로 함께 보장한다.

### `repositories`

- ORM 기반 DB 접근을 캡슐화한다.
- command 처리용 repository와 query projection 반영용 writer를 분리해 책임을 나눈다.

### `migrations`

- write 모델 스키마와 제약 조건 변화를 관리한다.
- 활성 세션 유니크, 점유/이력 단건 참조 같은 무결성 규칙이 여기에 반영된다.

## 클래스 및 모듈 설명

### 앱 설정과 라우팅

#### `ParkingCommandServiceConfig`

- 위치: [apps.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/apps.py)
- 역할:
  - Django 앱 이름과 기본 PK 타입을 등록한다.
- 구현 방식:
  - `AppConfig`를 상속한 최소 구성이다.
  - 별도 signal 등록이나 startup side effect는 두지 않는다.

#### `urlpatterns`

- 위치: [urls.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/urls.py)
- 역할:
  - `POST /api/parking/entry`
  - `POST /api/parking/exit`
- 구현 방식:
  - 두 API만 노출하는 단순 라우터다.
  - URL 단계에서는 분기 로직을 두지 않는다.

### View 계층

#### `ParkingEntryView`

- 위치: [parking_record_views.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/views/parking_record_views.py)
- 역할:
  - 입차 요청의 HTTP 진입점이다.
- 구현 방식:
  - `parse_entry_command()`로 요청 본문을 검증한다.
  - `get_parking_record_command_service()`로 service를 조립한다.
  - service 결과인 `ParkingRecordSnapshot`을 JSON으로 직렬화해 `201`을 반환한다.

#### `ParkingExitView`

- 위치: [parking_record_views.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/views/parking_record_views.py)
- 역할:
  - 출차 요청의 HTTP 진입점이다.
- 구현 방식:
  - `parse_exit_command()`로 입력을 검증한다.
  - service의 `create_exit()`를 호출한다.
  - 반환 스냅샷을 JSON으로 직렬화해 `200`을 반환한다.

### Serializer 계층

#### `parse_entry_command`

- 위치: [parking_record_serializers.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/serializers/parking_record_serializers.py)
- 역할:
  - 입차 요청 JSON을 `EntryCommand`로 변환한다.
- 구현 방식:
  - `_parse_json_body()`로 malformed JSON과 non-object body를 차단한다.
  - `_normalize_vehicle_num()`으로 차량 번호 정규화와 포맷 검증을 수행한다.
  - `_require_int()`로 `slot_id`를 정수로 강제한다.
  - `_parse_optional_datetime()`로 timezone-aware ISO 8601만 허용한다.
  - 검증 실패는 필드별 오류를 모아 `ValidationError`로 반환한다.

#### `parse_exit_command`

- 위치: [parking_record_serializers.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/serializers/parking_record_serializers.py)
- 역할:
  - 출차 요청 JSON을 `ExitCommand`로 변환한다.
- 구현 방식:
  - 차량 번호와 `exit_at`만 검증한다.
  - 입력 검증 규칙은 입차와 동일한 유틸리티를 재사용한다.

#### 내부 헬퍼 함수

- 위치: [parking_record_serializers.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/serializers/parking_record_serializers.py)
- `_parse_json_body`
  - JSON 디코딩과 최상위 객체 타입 검증을 담당한다.
- `_normalize_vehicle_num`
  - serializer 레벨에서 차량 번호 형식 오류를 필드 오류로 다시 매핑한다.
- `_require_int`
  - 필수 정수 필드 검증에 사용된다.
- `_parse_optional_datetime`
  - optional datetime 필드의 타입과 timezone-aware 여부를 검증한다.

### Service 계층

#### `ParkingRecordRepository` / `VehicleRepository` / `ParkingProjectionWriter`

- 위치: [parking_record_service.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/services/parking_record_service.py)
- 역할:
  - service가 구체 ORM 구현체에 직접 묶이지 않도록 최소 계약을 정의한다.
- 구현 방식:
  - `Protocol` 기반 인터페이스로 선언되어 테스트 대역 교체가 쉽다.
  - `ParkingProjectionWriter`는 command 성공 후 query projection 반영용 확장 지점이다.

#### `ParkingRecordCommandService`

- 위치: [parking_record_service.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/services/parking_record_service.py)
- 역할:
  - 입차/출차 유스케이스를 실행하는 핵심 애플리케이션 서비스다.
- 구현 방식:
  - `@transaction.atomic`으로 쓰기 유스케이스 전체를 하나의 트랜잭션으로 묶는다.
  - 생성자에서 repository와 projection writer를 주입받고, 기본값으로 Django 구현체를 사용한다.

주요 메서드:
- `create_entry`
  - 차량 존재 여부를 먼저 확인한다.
  - 슬롯과 점유 행을 `select_for_update()` 기반으로 잠근다.
  - 비활성 슬롯, 점유 중 슬롯, 동일 차량 활성 세션 존재 여부를 차단한다.
  - `ParkingHistory.start()`로 새 세션을 만들고 `SlotOccupancy.occupy()`로 현재 점유를 전환한다.
  - 저장이 끝나면 projection writer가 있으면 `record_entry()`를 호출한다.
  - DB 충돌은 `ParkingRecordConflictError`로 매핑한다.
- `create_exit`
  - 활성 세션을 차량 번호 기준으로 잠금 조회한다.
  - `ParkingHistory.exit()`로 이력을 종료한다.
  - `SlotOccupancy.release()`로 현재 점유를 해제한다.
  - 저장 후 projection writer가 있으면 `record_exit()`를 호출한다.

#### `_build_snapshot`

- 위치: [parking_record_service.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/services/parking_record_service.py)
- 역할:
  - 내부 도메인 모델을 API 응답용 write 스냅샷으로 축약한다.
- 구현 방식:
  - query 전용 필드 없이 write 결과만 담도록 고정한다.

### DTO 계층

#### `EntryCommand`

- 위치: [dtos.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/dtos.py)
- 역할:
  - 입차 처리에 필요한 입력값 묶음이다.
- 구현 방식:
  - 불변 `dataclass`로 정의되어 service에서 안전하게 사용된다.

#### `ExitCommand`

- 위치: [dtos.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/dtos.py)
- 역할:
  - 출차 처리에 필요한 입력값 묶음이다.

#### `ParkingRecordSnapshot`

- 위치: [dtos.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/dtos.py)
- 역할:
  - command API가 반환하는 write 결과 스냅샷이다.
- 구현 방식:
  - `to_dict()`에서 datetime을 ISO 8601 문자열로 변환한다.
  - query projection 정보는 의도적으로 포함하지 않는다.

### Domain Model 계층

#### `ParkingSlot`

- 위치: [parking_slot.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/models/parking_slot.py)
- 역할:
  - 주차 슬롯 마스터 정보와 활성 상태를 관리한다.
- 구현 방식:
  - `(zone_id, slot_code)` 유니크 제약으로 존 내 슬롯 코드 중복을 막는다.
  - `activate()`, `deactivate()` 같은 행위 중심 메서드만 제공한다.

#### `ParkingHistoryStatus`

- 위치: [enums.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/models/enums.py)
- 역할:
  - 주차 이력 상태를 `PARKED`, `EXITED` 두 값으로 고정한다.

#### `ParkingHistory`

- 위치: [parking_history.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/models/parking_history.py)
- 역할:
  - 차량의 주차 세션 이력을 표현한다.
- 구현 방식:
  - 활성 세션 기준으로 `vehicle_num`, `slot` 조건부 유니크 제약을 둔다.
  - `start()`에서 차량 번호를 정규화하고 초기 상태를 `PARKED`로 만든다.
  - `exit()`에서 중복 출차와 시간 역전을 도메인 레벨에서 차단한다.

#### `SlotOccupancy`

- 위치: [slot_occupancy.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/models/slot_occupancy.py)
- 역할:
  - 슬롯의 현재 점유 상태를 1행으로 유지하는 모델이다.
- 구현 방식:
  - `slot`은 `OneToOneField`라서 슬롯당 점유 행은 항상 하나다.
  - `history`도 `OneToOneField`라서 하나의 활성 이력이 여러 점유에 재사용되지 않는다.
  - 체크 제약으로 점유 시 필요한 필드가 함께 존재하도록 강제한다.
  - `occupy()`와 `release()`에서 상태 전이를 수행하고 `clean()`으로 일관성을 검증한다.

### Repository 계층

#### `DjangoParkingRecordRepository`

- 위치: [parking_record_repository.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/repositories/parking_record_repository.py)
- 역할:
  - command 처리에 필요한 write 모델 조회/저장을 담당한다.
- 구현 방식:
  - `get_slot_for_update()`
    - 대상 슬롯을 잠금 조회한다.
  - `get_or_create_occupancy_for_update()`
    - 점유 행이 없으면 만들고, 이후 잠금 조회한다.
  - `has_active_history_for_vehicle()`
    - 동일 차량의 활성 세션 존재 여부를 확인한다.
  - `get_active_history_for_vehicle_for_update()`
    - 출차 대상 활성 세션을 잠금 조회한다.
  - `save_history()`, `save_occupancy()`
    - `full_clean()` 후 저장해 모델 검증을 DB 저장 직전에 다시 통과시킨다.

#### `DjangoVehicleRepository`

- 위치: [vehicle_repository.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/repositories/vehicle_repository.py)
- 역할:
  - 차량 마스터 존재 여부 확인을 `vehicle_service`와 분리된 형태로 제공한다.
- 구현 방식:
  - 현재는 단순 존재 여부 조회만 제공한다.

#### `DjangoParkingProjectionWriter`

- 위치: [query_projection_repository.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/repositories/query_projection_repository.py)
- 역할:
  - command 성공 후 query side projection을 동기화한다.
- 구현 방식:
  - `record_entry()`
    - `CurrentParkingView`를 upsert한다.
    - 더 최신 `entry_at`이 이미 있으면 오래된 입차 반영을 건너뛴다.
    - 같은 존/슬롯 타입의 `ZoneAvailability`를 재계산한다.
  - `record_exit()`
    - 현재 projection이 같은 세션 또는 더 오래된 세션이면 삭제한다.
    - 이후 `ZoneAvailability`를 다시 계산한다.
  - `_sync_zone_availability()`
    - 증분 계산 대신 실제 `ParkingSlot`, `SlotOccupancy` 기준 count를 다시 계산해 drift를 줄인다.
  - `_get_slot_type_name()`
    - `zone_service.SlotType`에서 읽기 모델용 슬롯 타입명을 가져온다.
  - `_run_with_retry()`
    - SQLite 테스트 환경의 짧은 write lock만 제한적으로 재시도한다.

### 예외 계층

#### `ParkingRecordNotFoundError`

- 위치: [exceptions.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/exceptions.py)
- 역할:
  - 차량 미존재, 슬롯 미존재, 활성 세션 미존재 같은 경우를 `404`로 표현한다.

#### `ParkingRecordConflictError`

- 위치: [exceptions.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/exceptions.py)
- 역할:
  - 점유 충돌, 중복 세션, DB 경합 같은 경우를 `409`로 표현한다.

### 유틸리티 모듈

#### `normalize_vehicle_num`

- 위치: [vehicle_nums.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/vehicle_nums.py)
- 역할:
  - 저장/비교 기준 차량 번호를 표준 형태로 맞춘다.
- 구현 방식:
  - 공백, 하이픈을 제거하고 대문자로 정규화한다.
  - 정규식 `^\d{2,3}[가-힣]\d{4}$`로 형식을 검증한다.

## 의존성 조립 방식

`get_parking_record_command_service()`는 현재 command service의 기본 조립 지점이다.

- 위치: [dependencies.py](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/src/parking_command_service/dependencies.py)
- 조립 대상:
  - `DjangoParkingRecordRepository`
  - `DjangoVehicleRepository`
  - `DjangoParkingProjectionWriter`

이 구조의 의도:
- view가 구체 ORM 클래스 생성 책임을 직접 갖지 않게 한다.
- unit test에서는 mock repository를 쉽게 주입할 수 있게 한다.
- projection writer를 선택적으로 교체하거나 제거하기 쉬운 구조를 유지한다.

## 입차/출차 구현 흐름

### 입차

1. `ParkingEntryView.post()`가 요청을 받는다.
2. `parse_entry_command()`가 JSON과 필드를 검증한다.
3. `ParkingRecordCommandService.create_entry()`가 트랜잭션을 시작한다.
4. 차량 존재 여부, 슬롯 존재 여부, 슬롯 활성 여부, 점유 여부, 차량 중복 세션 여부를 점검한다.
5. `ParkingHistory.start()`로 활성 이력을 만든다.
6. `SlotOccupancy.occupy()`로 현재 점유를 전환한다.
7. repository가 `full_clean()` 후 저장한다.
8. projection writer가 `CurrentParkingView`, `ZoneAvailability`를 갱신한다.
9. `ParkingRecordSnapshot`이 JSON 응답으로 반환된다.

### 출차

1. `ParkingExitView.post()`가 요청을 받는다.
2. `parse_exit_command()`가 요청을 검증한다.
3. `ParkingRecordCommandService.create_exit()`가 활성 이력을 잠금 조회한다.
4. `ParkingHistory.exit()`로 세션을 종료한다.
5. `SlotOccupancy.release()`로 현재 점유를 해제한다.
6. repository가 저장한다.
7. projection writer가 현재 위치 projection을 제거하고 zone 가용 현황을 재계산한다.
8. 종료된 `ParkingRecordSnapshot`이 응답된다.

## 구현 특징과 주의점

- command 응답은 write 스냅샷만 반환한다.
- 조회 전용 필드 조합은 query projection에서 담당한다.
- 도메인 규칙은 모델 메서드와 DB 제약을 같이 사용해 이중으로 보호한다.
- 동시성 제어는 `select_for_update()`와 조건부 유니크 제약을 기본으로 한다.
- 현재 projection writer는 query 서비스 모델을 직접 갱신한다.
  - 즉, 완전한 비동기 이벤트 기반 구조라기보다 same-process 동기화 방식이다.
- `slot_type_id`와 차량 타입 적합성 규칙은 아직 구현 범위에 없다.

## 관련 문서

- [parking-command-entities.md](/Users/kyum/Desktop/Private/autoE/docs/entities/parking-command-entities.md)
- [TEST_SPEC_PARKING_RECORD_API.md](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/test/TEST_SPEC_PARKING_RECORD_API.md)
- [TEST_EXECUTION_PARKING_RECORD_API.md](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/test/TEST_EXECUTION_PARKING_RECORD_API.md)
- [TEST_EXECUTION_PARKING_RECORD_API_FOLLOW_UP.md](/Users/kyum/Desktop/Private/autoE/services/parking-command-service/test/TEST_EXECUTION_PARKING_RECORD_API_FOLLOW_UP.md)
