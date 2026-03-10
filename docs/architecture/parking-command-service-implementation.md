# parking-command-service 패키지/클래스 구현 설명

## 목적

- `parking_command_service`의 현재 구현 구조를 DDD 기준으로 설명한다.
- 글로벌 공통 영역과 `parking_record` 도메인 영역의 책임 분리를 한 번에 확인할 수 있도록 정리한다.

## 현재 구조

`parking_command_service`는 CQRS 기준에서 write 모델을 담당하는 Django 앱이다.

현재 코드는 크게 세 층으로 나뉜다.

- 루트 Django 진입점
- `global_shared`
- `domains/parking_record`

핵심 흐름:
1. 루트 urls.py가 도메인 HTTP 라우터를 연결한다.
2. presentation/http/views.py가 요청을 받는다.
3. presentation/http/serializers.py가 JSON을 command DTO로 변환한다.
4. application/services.py가 트랜잭션 안에서 유스케이스를 실행한다.
5. infrastructure/repositories/*가 DB 접근과 projection 반영을 수행한다.
6. domain/*가 도메인 상태 전이와 불변식을 보장한다.

## 패키지별 책임

### 루트 패키지

- apps.py
  - Django 앱 등록 정보만 가진다.
- urls.py
  - 도메인 HTTP URL을 루트에서 include 하는 진입점이다.
- models/__init__.py
  - Django model autodiscovery를 위해 도메인 모델을 다시 노출한다.

루트에는 더 이상 비즈니스 로직을 두지 않는다.

### `global_shared`

도메인에 종속되지 않는 공통 기능을 둔다.

- global_shared/application/dependencies.py
  - 애플리케이션 조립 지점
- global_shared/utils/vehicle_nums.py
  - 차량 번호 정규화 공통 유틸리티

### `domains/parking_record`

입차/출차 기록 도메인의 실제 구현을 모은다.

- `application`
  - 유스케이스, DTO, 애플리케이션 예외
- `domain`
  - 엔터티, 상태 전이, 불변식
- `infrastructure`
  - ORM repository, 외부 모델 연동
- `presentation`
  - HTTP serializer, view, URL

## 클래스 및 모듈 설명

### 루트 진입점

#### `ParkingCommandServiceConfig`

- 위치: apps.py
- 역할:
  - Django 앱 이름과 기본 PK 타입을 등록한다.

#### 루트 `urlpatterns`

- 위치: urls.py
- 역할:
  - `parking_record` 도메인의 HTTP URL을 외부에 노출한다.
- 구현 방식:
  - 도메인 presentation 계층의 URL만 연결한다.

#### 루트 `models`

- 위치: models/__init__.py
- 역할:
  - Django가 `parking_command_service` 앱의 모델을 인식하도록 도메인 모델을 재노출한다.
- 구현 방식:
  - 실 구현은 도메인 패키지에 두고, 루트 `models`는 얇은 진입점으로만 유지한다.

### Global Shared

#### `get_parking_record_command_service`

- 위치: dependencies.py
- 역할:
  - `parking_record` 유스케이스 실행에 필요한 구현체를 조립한다.
- 구현 방식:
  - `DjangoParkingRecordRepository`
  - `DjangoVehicleRepository`
  - `DjangoParkingProjectionWriter`
  - 위 3개를 `ParkingRecordCommandService`에 주입한다.

#### `normalize_vehicle_num`

- 위치: vehicle_nums.py
- 역할:
  - 차량 번호 저장/비교 기준을 표준 형태로 맞춘다.
- 구현 방식:
  - 공백, 하이픈 제거
  - 대문자 변환
  - 정규식 `^\d{2,3}[가-힣]\d{4}$` 검증

### Domain: `parking_record/application`

#### `EntryCommand`

- 위치: dtos.py
- 역할:
  - 입차 처리 입력 DTO
- 구현 방식:
  - 공통 슬롯 식별값 `vehicle_num`, `zone_id`, `slot_code`, `slot_id`를 함께 가진다.
  - `entry_at`만 입차 전용 필드로 추가한다.

#### `ExitCommand`

- 위치: dtos.py
- 역할:
  - 출차 처리 입력 DTO
- 구현 방식:
  - 입차와 같은 슬롯 식별값을 사용해 현재 활성 세션과 요청 위치가 일치하는지 검증할 수 있게 한다.
  - `exit_at`만 출차 전용 필드로 추가한다.

#### `ParkingRecordSnapshot`

- 위치: dtos.py
- 역할:
  - command API 응답용 write 스냅샷
- 구현 방식:
  - `zone_id`, `slot_code`, `slot_id`를 모두 포함해 프론트가 점유 위치를 바로 표시할 수 있게 한다.
  - `to_dict()`에서 datetime을 ISO 8601 문자열로 변환한다.
  - query projection 전용 필드는 포함하지 않는다.

#### `ParkingRecordNotFoundError`

- 위치: exceptions.py
- 역할:
  - 차량 미존재, 슬롯 미존재, 활성 세션 미존재를 `404` 의미로 표현한다.

#### `ParkingRecordConflictError`

- 위치: exceptions.py
- 역할:
  - 점유 충돌, 중복 세션, DB 경합을 `409` 의미로 표현한다.

#### `ParkingRecordRepository` / `VehicleRepository` / `ParkingProjectionWriter`

- 위치: services.py
- 역할:
  - application service가 인프라 구현체에 직접 고정되지 않도록 최소 계약을 제공한다.
- 구현 방식:
  - `Protocol` 기반 인터페이스로 정의한다.

#### `ParkingRecordCommandService`

- 위치: services.py
- 역할:
  - 입차/출차 유스케이스를 실행하는 애플리케이션 서비스다.
- 구현 방식:
  - `create_entry()`
    - DB lock 예외를 짧게 재시도한다.
    - 실제 유스케이스는 `_create_entry_once()`에서 `transaction.atomic()`으로 실행한다.
    - 차량 존재 여부, 슬롯 상태, 중복 활성 세션을 검증한다.
    - `ParkingHistory.start()`와 `SlotOccupancy.occupy()`를 조합한다.
    - 성공 후 projection writer가 있으면 `record_entry()`를 호출한다.
  - `create_exit()`
    - 활성 세션을 조회한다.
    - `ParkingHistory.exit()`와 `SlotOccupancy.release()`를 실행한다.
    - 성공 후 projection writer가 있으면 `record_exit()`를 호출한다.

### Domain: `parking_record/domain`

#### `ParkingHistoryStatus`

- 위치: enums.py
- 역할:
  - `PARKED`, `EXITED` 상태를 정의한다.

#### `ParkingSlot`

- 위치: parking_slot.py
- 역할:
  - 슬롯 마스터와 활성 상태를 표현한다.
- 구현 방식:
  - `(zone_id, slot_code)` 유니크 제약을 둔다.
  - `activate()`, `deactivate()` 행위 메서드를 제공한다.

#### `ParkingHistory`

- 위치: parking_history.py
- 역할:
  - 차량의 주차 세션 이력을 표현한다.
- 구현 방식:
  - 활성 세션 기준으로 차량별/슬롯별 유니크 제약을 둔다.
  - `start()`에서 차량 번호를 정규화하고 `PARKED` 상태로 시작한다.
  - `exit()`에서 중복 출차와 시간 역전을 도메인에서 차단한다.

#### `SlotOccupancy`

- 위치: slot_occupancy.py
- 역할:
  - 슬롯의 현재 점유 상태를 1행으로 유지한다.
- 구현 방식:
  - `slot`은 `OneToOneField`라서 슬롯당 점유 행은 하나만 존재한다.
  - `history`도 `OneToOneField`라서 같은 이력이 여러 점유에 재사용되지 않는다.
  - `occupy()`와 `release()`에서 상태 전이를 수행한다.
  - `clean()`에서 점유/이력/슬롯 일관성을 다시 검증한다.

### Domain: `parking_record/infrastructure`

#### `DjangoParkingRecordRepository`

- 위치: parking_record_repository.py
- 역할:
  - command 처리에 필요한 write 모델 조회/저장을 담당한다.
- 구현 방식:
  - `select_for_update()` 기반 슬롯/이력 잠금 조회
  - `get_or_create()` 기반 점유 행 보장
  - `save_*()`에서 `full_clean()` 후 저장

#### `DjangoVehicleRepository`

- 위치: Vehicle_repository.py
- 역할:
  - `vehicle_service`의 차량 존재 여부 조회를 캡슐화한다.

#### `DjangoParkingProjectionWriter`

- 위치: query_projection_repository.py
- 역할:
  - command 성공 후 query projection을 동기화한다.
- 구현 방식:
  - `record_entry()`
    - `CurrentParkingView` upsert
    - `slot_id`, `zone_id`, `slot_code`를 함께 저장
    - 오래된 입차는 최신 projection을 덮어쓰지 않음
    - `ZoneAvailability` 재계산
  - `record_exit()`
    - 현재 projection 삭제
    - `ZoneAvailability` 재계산
  - `_run_with_retry()`
    - SQLite 테스트 환경의 짧은 lock만 제한적으로 재시도

### Domain: `parking_record/presentation/http`

#### `parse_entry_command`

- 위치: serializers.py
- 역할:
  - 입차 요청 JSON을 `EntryCommand`로 변환한다.
- 구현 방식:
  - malformed JSON 차단
  - JSON object만 허용
  - `vehicle_num`, `zone_id`, `slot_code`, `slot_id`, `entry_at` 검증
  - `slot_code`는 빈 값, 앞뒤 공백, 소문자 입력을 허용하지 않는다.
  - 필드 오류를 모아 `ValidationError`로 반환

#### `parse_exit_command`

- 위치: serializers.py
- 역할:
  - 출차 요청 JSON을 `ExitCommand`로 변환한다.
- 구현 방식:
  - 입차와 같은 슬롯 식별 필드를 동일하게 검증한다.
  - `exit_at`이 주어지면 timezone-aware datetime인지 확인한다.

#### `ParkingEntryView`

- 위치: views.py
- 역할:
  - 입차 HTTP 진입점
- 구현 방식:
  - serializer로 command 생성
  - `global_shared` 조립 지점에서 service 획득
  - snapshot을 `201` JSON 응답으로 반환

#### `ParkingExitView`

- 위치: views.py
- 역할:
  - 출차 HTTP 진입점

#### 도메인 HTTP `urlpatterns`

- 위치: urls.py
- 역할:
  - `POST /api/parking/entry`
  - `POST /api/parking/exit`

## 의도한 분리 기준

### 글로벌 공통

- 여러 도메인에서 재사용 가능한 조립/유틸리티
- 현재는 차량 번호 정규화, 의존성 조립만 여기에 있다

### 도메인 전용

- `parking_record` 도메인에만 의미가 있는 DTO, 모델, repository, view
- 다른 도메인이 이 내부 구현 세부에 직접 의존하지 않도록 분리했다

## 입차/출차 흐름

### 입차

1. 루트 URL이 `parking_record.presentation.http.urls`로 라우팅한다.
2. `ParkingEntryView.post()`가 요청을 받는다.
3. `parse_entry_command()`가 JSON과 필드를 검증한다.
   - `slot_id`와 `zone_id + slot_code`는 이후 service에서 동일 슬롯인지 다시 검증한다.
4. `get_parking_record_command_service()`가 repository와 projection writer를 조립한다.
5. `ParkingRecordCommandService.create_entry()`가 트랜잭션 안에서 이력 생성과 점유 전환을 수행한다.
6. `DjangoParkingProjectionWriter.record_entry()`가 query projection을 갱신한다.
7. `ParkingRecordSnapshot`이 응답으로 반환된다.

### 출차

1. `ParkingExitView.post()`가 요청을 받는다.
2. `parse_exit_command()`가 요청을 검증한다.
3. `ParkingRecordCommandService.create_exit()`가 차량의 활성 이력과 요청 위치가 일치하는지 확인한 뒤 점유를 해제한다.
4. `DjangoParkingProjectionWriter.record_exit()`가 현재 위치 projection을 제거한다.
5. 종료된 snapshot이 응답으로 반환된다.

