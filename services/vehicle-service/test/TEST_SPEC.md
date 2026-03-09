# vehicle-service 테스트 명세 (엔터티 빠른 고정)

## 1. 목적

- `VEHICLE` 엔터티와 차량 타입 규칙을 빠르게 확정한다.
- 등록/조회/타입 변경 핵심 흐름만 AT로 검증한다.

## 2. 인수 테스트 (AT)

### AT-VH-CORE-01 차량 등록 + 조회
- Given: 신규 차량번호.
- When: 등록 후 단건 조회.
- Then: 저장된 차량번호/타입이 일치한다.
- 추천 메서드명: `test_register_and_find_vehicle()`

### AT-VH-CORE-02 중복 등록 거부
- Given: 이미 등록된 차량번호.
- When: 동일 번호로 재등록.
- Then: 409 반환.
- 추천 메서드명: `test_reject_duplicate_vehicle_registration()`

### AT-VH-CORE-03 타입 변경 가드레일
- Given: 등록된 차량.
- When: 유효 타입/무효 타입으로 변경 요청.
- Then: 유효 요청은 성공, 무효 요청은 400.
- 추천 메서드명: `test_change_vehicle_type_or_reject_invalid()`

## 3. 계약 테스트 (CT)

### CT-VH-CORE-01 등록/조회 스키마
- Given: 등록/조회 API 호출.
- When: 요청/응답을 검증.
- Then: 필수 필드와 enum 계약을 만족한다.
- 추천 메서드명: `test_match_vehicle_schema_contract()`

### CT-VH-CORE-02 오류 코드 계약
- Given: 중복/미존재/유효성 오류 조건.
- When: API 호출.
- Then: 409/404/400 계약 유지.
- 추천 메서드명: `test_preserve_vehicle_error_status_contract()`

## 4. 단위 테스트 (UT)

### UT-VH-ENTITY-01 생성 규칙
- Given: 유효/무효 차량번호 입력.
- When: `Vehicle.create()` 호출.
- Then: 무효 값은 거부된다.
- 추천 메서드명: `test_validate_vehicle_num_on_create()`

### UT-VH-ENTITY-02 타입 변경 규칙
- Given: 기존 차량 엔터티.
- When: `changeType()` 호출.
- Then: null/미지원 타입은 거부된다.
- 추천 메서드명: `test_validate_vehicle_type_on_change()`

### UT-VH-ENTITY-03 enum 매핑
- Given: DB 문자열과 도메인 enum.
- When: 매핑 수행.
- Then: 양방향 매핑이 안정적으로 동작한다.
- 추천 메서드명: `test_map_vehicle_type_enum_bidirectionally()`

## 5. 저장소/DB 제약 테스트 (RT)

### RT-VH-DB-01 PK 유일성
- Given: 동일 `vehicle_num` 중복 저장.
- When: 저장한다.
- Then: 중복 저장 실패.
- 추천 메서드명: `test_fail_duplicate_vehicle_num_persist()`

### RT-VH-DB-02 타입 제약
- Given: enum 외 타입 문자열 저장 시도.
- When: 저장한다.
- Then: 제약 위반으로 실패.
- 추천 메서드명: `test_fail_unknown_vehicle_type_persist()`
