# zone-service 테스트 명세 (엔터티 빠른 고정)

## 1. 목적

- `ZONE`, `SLOT_TYPE` 마스터 엔터티를 빠르게 확정한다.
- 생성/조회/중복 방지 핵심 흐름만 AT로 검증한다.

## 2. 인수 테스트 (AT)

### AT-ZN-CORE-01 존 생성 + 목록 조회
- Given: 신규 존 이름.
- When: 존을 생성하고 목록 조회.
- Then: 생성된 존이 목록에 포함된다.
- 추천 메서드명: `test_create_zone_and_list()`

### AT-ZN-CORE-02 존명 중복 거부
- Given: 동일 `zone_name`이 존재한다.
- When: 같은 이름으로 생성.
- Then: 409 반환.
- 추천 메서드명: `test_reject_duplicate_zone_name()`

### AT-ZN-CORE-03 슬롯타입 생성 가드레일
- Given: 신규/중복 타입명.
- When: 슬롯타입 생성.
- Then: 신규는 성공, 중복은 409.
- 추천 메서드명: `test_create_slot_type_or_reject_duplicate()`

## 3. 계약 테스트 (CT)

### CT-ZN-CORE-01 존 API 스키마
- Given: 존 생성/목록 조회.
- When: 요청/응답 검증.
- Then: 필수 필드 계약 유지.
- 추천 메서드명: `test_match_zone_api_schema()`

### CT-ZN-CORE-02 슬롯타입 API 계약
- Given: 슬롯타입 생성 호출.
- When: 요청/응답 검증.
- Then: 타입 문자열 규칙 및 오류 포맷 계약 유지.
- 추천 메서드명: `test_match_slot_type_api_contract()`

## 4. 단위 테스트 (UT)

### UT-ZN-ENTITY-01 Zone 생성 규칙
- Given: 유효/무효 `zone_name`.
- When: `Zone.create()` 호출.
- Then: 공백/널은 거부된다.
- 추천 메서드명: `test_validate_zone_name_on_create()`

### UT-ZN-ENTITY-02 Zone 변경 규칙
- Given: 기존 Zone.
- When: `rename()` 호출.
- Then: 동일 이름/무효 이름 정책을 지킨다.
- 추천 메서드명: `test_apply_zone_rename_policy()`

### UT-ZN-ENTITY-03 SlotType 정규화 규칙
- Given: 대소문자/공백이 섞인 타입명.
- When: `SlotType.create()` 호출.
- Then: 정책대로 정규화된다.
- 추천 메서드명: `test_normalize_slot_type_name_on_create()`

## 5. 저장소/DB 제약 테스트 (RT)

### RT-ZN-DB-01 존 이름 유니크
- Given: 동일 `zone_name` 저장 시도.
- When: 저장한다.
- Then: 중복 실패.
- 추천 메서드명: `test_fail_duplicate_zone_name_persist()`

### RT-ZN-DB-02 슬롯타입 유니크
- Given: 동일 `type` 저장 시도.
- When: 저장한다.
- Then: 중복 실패.
- 추천 메서드명: `test_fail_duplicate_slot_type_persist()`
