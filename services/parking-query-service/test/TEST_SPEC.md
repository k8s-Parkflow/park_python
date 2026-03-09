# parking-query-service 테스트 명세 인덱스

## 목적

- `parking-query-service`의 테스트 명세는 기능 단위로 분리해 관리한다.
- 각 기능은 독립적인 `TEST_SPEC_<FEATURE>.md` 파일을 가지며, AC와 `AT/CT/UT/RT`를 1:1로 추적 가능해야 한다.

## 기능별 TEST_SPEC

- 차량 번호 기반 현재 위치 조회: [TEST_SPEC_CURRENT_LOCATION_BY_VEHICLE.md](/Users/kyum/Desktop/Private/autoE/services/parking-query-service/test/TEST_SPEC_CURRENT_LOCATION_BY_VEHICLE.md)
- 타입별 전체 Zone 여석 총합 조회: [TEST_SPEC_ZONE_TOTAL_AVAILABILITY.md](/Users/kyum/Desktop/Private/autoE/services/parking-query-service/test/TEST_SPEC_ZONE_TOTAL_AVAILABILITY.md)

## 공통 규칙

- 테스트 작성 순서는 `Acceptance -> Contract -> Unit -> Repository/DB -> 최소 구현 -> 리팩터링`을 따른다.
- 테스트 코드는 `Given / When / Then` 주석 구조를 사용한다.
- DisplayName은 `[ID] 기대 결과` 형식을 따른다.
- 메서드명은 `should_<then>__when_<when>` 형식을 따른다.
- 시간 값은 timezone-aware 값만 사용한다.
