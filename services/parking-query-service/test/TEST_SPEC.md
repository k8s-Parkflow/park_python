# parking-query-service 테스트 명세

## 1. 목적

- `parking-query-service`의 조회 기능을 TDD 순서로 안전하게 확장한다.
- 이번 턴의 신규 범위는 `타입별 전체 Zone 여석 총합 조회` 기능이다.
- 현재 RED 범위는 `slot_type` 미지정 시 전체 타입 여석 총합 조회까지 확장된 상태다.

## 2. 공통 규칙

- 테스트 작성 순서는 `Acceptance -> Contract -> Unit -> Repository/DB -> 최소 구현 -> 리팩터링`을 따른다.
- 테스트 코드는 `Given / When / Then` 주석 구조를 사용한다.
- DisplayName은 `[ID] 기대 결과` 형식을 따른다.
- 메서드명은 `should_<then>__when_<when>` 형식을 따른다.
- 시간 값은 timezone-aware 값만 사용한다.

## 3. 공통 도메인 가정

- 조회 대상 Zone은 등록된 전체 Zone이다.
- 타입별 잔여석은 `parking_query_service.ZoneAvailability.available_count`를 기준으로 계산한다.
- 타입별 전체 잔여석은 전체 Zone에 속한 동일 타입 `available_count` 합계다.
- `slot_type`가 비어 있으면 지원하는 전체 타입의 `available_count` 합계를 반환한다.
- 응답은 Zone별 상세 목록이 아니라 타입별 총합 한 건만 반환한다.
- 잘못된 타입 요청은 표준 에러 포맷의 `400 bad_request`를 반환한다.

## 4. 목표 계약 초안

### 4.1 타입별 전체 Zone 여석 총합 조회

- `GET /api/zones/availabilities?slot_type={GENERAL|EV|DISABLED}`
- 응답 예시

```json
{
  "slotType": "GENERAL",
  "availableCount": 12
}
```

### 4.2 오류 응답

- `GET /api/zones/availabilities?slot_type=VIP`

```json
{
  "error": {
    "code": "bad_request",
    "message": "잘못된 요청입니다.",
    "details": {
      "slot_type": [
        "지원하지 않는 슬롯 타입입니다."
      ]
    }
  }
}
```

### 4.3 전체 타입 총합 응답

- `GET /api/zones/availabilities`

```json
{
  "availableCount": 23
}
```

## 5. 기능 A: 차량 현재 위치 조회

### 5.1 인수 테스트 (AT)

#### AT-PQ-CORE-01 차량 현재 위치 조회

- Given: 차량이 주차 중이거나 주차 중이 아닌 상태다.
- When: 차량 번호로 현재 위치를 조회한다.
- Then: 존재 시 현재 위치를 반환하고, 미존재 시 404를 반환한다.
- 추천 메서드명: `should_return_location_or_404__when_vehicle_num_requested()`

#### AT-PQ-CORE-02 최신 상태 반영

- Given: 동일 차량에 대해 오래된 업데이트와 최신 업데이트가 있다.
- When: 현재 위치를 조회한다.
- Then: 최신 `updated_at` 기준 데이터가 반환된다.
- 추천 메서드명: `should_return_latest_projection__when_multiple_updates_exist()`

### 5.2 계약 테스트 (CT)

#### CT-PQ-CORE-01 조회 응답 스키마

- Given: 정상 조회가 가능한 현재 위치 데이터가 있다.
- When: `/parking/current/{vehicleNum}`를 호출한다.
- Then: 필수 필드와 타입 계약을 만족한다.
- 추천 메서드명: `should_match_current_parking_response_schema__when_request_succeeds()`

#### CT-PQ-CORE-02 오류 응답 계약

- Given: 미존재 차량 번호로 조회를 요청한다.
- When: `/parking/current/{vehicleNum}`를 호출한다.
- Then: 404와 표준 오류 응답 포맷을 유지한다.
- 추천 메서드명: `should_preserve_not_found_error_contract__when_vehicle_missing()`

### 5.3 단위 테스트 (UT)

#### UT-PQ-VIEW-01 현재위치 upsert/delete

- Given: 동일 차량 데이터가 반복 반영되고 이후 출차 이벤트가 반영된다.
- When: 프로젝션 갱신 로직을 적용한다.
- Then: 최신 상태로 유지되고 출차 시 제거된다.
- 추천 메서드명: `should_upsert_latest_and_delete_on_exit__when_projection_applied()`

#### UT-PQ-VIEW-02 시간 역전 보호

- Given: 최신 데이터 이후에 과거 타임스탬프 업데이트가 들어온다.
- When: 프로젝션 갱신 로직을 적용한다.
- Then: 현재 최신 상태를 과거 데이터가 덮어쓰지 못한다.
- 추천 메서드명: `should_ignore_stale_projection_update__when_older_event_received()`

### 5.4 저장소/DB 테스트 (RT)

#### RT-PQ-DB-01 현재위치 PK

- Given: 동일 `vehicle_num`의 현재 위치 데이터가 중복 저장된다.
- When: 저장을 시도한다.
- Then: PK 제약으로 실패한다.
- 추천 메서드명: `should_fail_duplicate_vehicle_num_insert__when_primary_key_conflicts()`

## 6. 기능 B: 타입별 전체 Zone 여석 총합 조회

### 6.1 Acceptance Criteria

#### AC-PQ-ZONE-01 전체 Zone 일반 타입 여석 총합 조회

- 사용자가 일반 타입 여석 조회를 요청하면 전체 Zone의 일반 타입 잔여석 총합을 반환한다.
- 반환 값은 전체 Zone의 일반 타입 `available_count` 합계와 일치해야 한다.

#### AC-PQ-ZONE-02 전체 Zone 전기차 타입 여석 총합 조회

- 사용자가 전기차 타입 여석 조회를 요청하면 전체 Zone의 전기차 타입 잔여석 총합을 반환한다.
- 반환 값은 전체 Zone의 전기차 타입 `available_count` 합계와 일치해야 한다.

#### AC-PQ-ZONE-03 전체 Zone 장애인 타입 여석 총합 조회

- 사용자가 장애인 타입 여석 조회를 요청하면 전체 Zone의 장애인 타입 잔여석 총합을 반환한다.
- 반환 값은 전체 Zone의 장애인 타입 `available_count` 합계와 일치해야 한다.

#### AC-PQ-ZONE-04 지원하지 않는 타입 예외 처리

- 지원하지 않는 타입으로 요청하면 400과 표준 오류 포맷을 반환한다.

#### AC-PQ-ZONE-05 전체 타입 여석 총합 조회

- 사용자가 `slot_type` 없이 조회를 요청하면 전체 Zone의 전체 타입 잔여석 총합을 반환한다.
- 반환 값은 전체 Zone의 `GENERAL`, `EV`, `DISABLED` 타입 `available_count` 합계와 일치해야 한다.

#### AC-PQ-ZONE-06 데이터 없는 타입 0 반환

- 지원하는 타입으로 조회했지만 집계 데이터가 하나도 없으면 `0`을 반환한다.
- 오류 응답이 아니라 정상 응답으로 처리해야 한다.

#### AC-PQ-ZONE-07 전체 조회 시 데이터 없는 타입 포함 합산

- `slot_type` 없이 조회할 때 일부 타입 집계 데이터가 없어도 존재하는 타입만 합산해 정상 응답을 반환한다.
- 집계가 없는 타입은 `0`으로 간주한다.

#### AC-PQ-ZONE-08 음수 잔여석 불가

- 반환되는 잔여석은 음수가 될 수 없다.
- `available_count = total_count - occupied_count` 불변식을 위반하지 않아야 한다.

#### AC-PQ-ZONE-09 입력 정규화 정책

- 지원하는 타입 값은 대소문자를 구분하지 않고 허용한다.
- 응답의 `slotType`은 표준 대문자 값으로 반환한다.

### 6.2 인수 테스트 (AT)

#### AT-PQ-ZONE-01 일반 타입 총합 조회

- Given: 전체 Zone과 일반 타입 집계 데이터가 존재한다.
- When: `slot_type=GENERAL`로 조회를 요청한다.
- Then: 전체 Zone의 일반 타입 잔여석 총합을 반환한다.
- 추천 메서드명: `should_return_total_general_available_count_for_all_zones__when_general_slot_type_requested()`

#### AT-PQ-ZONE-02 전기차 타입 총합 조회

- Given: 전체 Zone과 전기차 타입 집계 데이터가 존재한다.
- When: `slot_type=EV`로 조회를 요청한다.
- Then: 전체 Zone의 전기차 타입 잔여석 총합을 반환한다.
- 추천 메서드명: `should_return_total_ev_available_count_for_all_zones__when_ev_slot_type_requested()`

#### AT-PQ-ZONE-03 장애인 타입 총합 조회

- Given: 전체 Zone과 장애인 타입 집계 데이터가 존재한다.
- When: `slot_type=DISABLED`로 조회를 요청한다.
- Then: 전체 Zone의 장애인 타입 잔여석 총합을 반환한다.
- 추천 메서드명: `should_return_total_disabled_available_count_for_all_zones__when_disabled_slot_type_requested()`

#### AT-PQ-ZONE-04 잘못된 타입 요청

- Given: 지원하지 않는 `slot_type` 값을 전달한다.
- When: 조회를 요청한다.
- Then: 400과 표준 오류 응답을 반환한다.
- 추천 메서드명: `should_return_bad_request__when_unsupported_slot_type_requested()`

#### AT-PQ-ZONE-05 전체 타입 총합 조회

- Given: 전체 Zone과 각 타입 집계 데이터가 존재한다.
- When: `slot_type` 없이 조회를 요청한다.
- Then: 전체 Zone의 전체 타입 잔여석 총합을 반환한다.
- 추천 메서드명: `should_return_total_available_count_for_all_slot_types__when_slot_type_not_provided()`

#### AT-PQ-ZONE-06 데이터 없는 타입 0 반환

- Given: 지원하는 타입이지만 집계 데이터가 하나도 없다.
- When: 해당 타입으로 조회를 요청한다.
- Then: `availableCount=0`을 반환한다.
- 추천 메서드명: `should_return_zero_available_count__when_supported_slot_type_has_no_projection()`

#### AT-PQ-ZONE-07 전체 조회 시 누락 타입 포함 합산

- Given: 전체 조회 대상 데이터 중 일부 타입 집계가 비어 있다.
- When: `slot_type` 없이 조회를 요청한다.
- Then: 존재하는 타입만 합산한 전체 잔여석을 반환한다.
- 추천 메서드명: `should_return_total_available_count__when_some_slot_types_have_no_projection()`

#### AT-PQ-ZONE-09 입력 정규화

- Given: 지원하는 타입을 소문자 또는 혼합 대소문자로 전달한다.
- When: 조회를 요청한다.
- Then: 표준 대문자 타입으로 정규화되어 정상 응답을 반환한다.
- 추천 메서드명: `should_return_normalized_slot_type__when_slot_type_requested_with_mixed_case()`

### 6.3 계약 테스트 (CT)

#### CT-PQ-ZONE-01 일반 타입 총합 응답 스키마

- Given: 일반 타입 총합 조회가 가능한 데이터가 있다.
- When: `GET /api/zones/availabilities?slot_type=GENERAL`를 호출한다.
- Then: `slotType`, `availableCount` 필드와 각 필드 타입 계약을 만족한다.
- 추천 메서드명: `should_match_total_typed_availability_response_schema__when_general_slot_type_requested()`

#### CT-PQ-ZONE-02 전기차 타입 총합 응답 스키마

- Given: 전기차 타입 총합 조회가 가능한 데이터가 있다.
- When: `GET /api/zones/availabilities?slot_type=EV`를 호출한다.
- Then: `slotType`, `availableCount` 필드와 각 필드 타입 계약을 만족한다.
- 추천 메서드명: `should_match_total_typed_availability_response_schema__when_ev_slot_type_requested()`

#### CT-PQ-ZONE-03 장애인 타입 총합 응답 스키마

- Given: 장애인 타입 총합 조회가 가능한 데이터가 있다.
- When: `GET /api/zones/availabilities?slot_type=DISABLED`를 호출한다.
- Then: `slotType`, `availableCount` 필드와 각 필드 타입 계약을 만족한다.
- 추천 메서드명: `should_match_total_typed_availability_response_schema__when_disabled_slot_type_requested()`

#### CT-PQ-ZONE-04 오류 응답 계약

- Given: 지원하지 않는 `slot_type`로 요청한다.
- When: `GET /api/zones/availabilities?slot_type=VIP`를 호출한다.
- Then: 400과 표준 오류 응답 포맷을 유지한다.
- 추천 메서드명: `should_preserve_bad_request_error_contract__when_slot_type_invalid()`

#### CT-PQ-ZONE-05 전체 타입 총합 응답 스키마

- Given: 전체 타입 총합 조회가 가능한 데이터가 있다.
- When: `GET /api/zones/availabilities`를 호출한다.
- Then: `availableCount` 필드만 가지는 응답 계약을 만족한다.
- 추천 메서드명: `should_match_total_availability_response_schema__when_slot_type_not_provided()`

#### CT-PQ-ZONE-06 데이터 없는 타입 0 응답 스키마

- Given: 지원하는 타입이지만 집계 데이터가 없다.
- When: 해당 타입으로 조회를 요청한다.
- Then: 정상 응답과 기존 타입별 스키마 계약을 유지한다.
- 추천 메서드명: `should_preserve_typed_availability_response_schema__when_supported_slot_type_has_no_projection()`

#### CT-PQ-ZONE-07 전체 조회 누락 타입 응답 스키마

- Given: 일부 타입 집계가 비어 있다.
- When: `GET /api/zones/availabilities`를 호출한다.
- Then: `availableCount` 단일 필드 응답 계약을 유지한다.
- 추천 메서드명: `should_preserve_total_availability_response_schema__when_some_slot_types_have_no_projection()`

#### CT-PQ-ZONE-09 입력 정규화 응답 스키마

- Given: 지원하는 타입을 대소문자가 섞인 값으로 전달한다.
- When: 조회를 요청한다.
- Then: 응답은 정상 타입별 스키마를 유지하고 `slotType`은 표준 대문자다.
- 추천 메서드명: `should_preserve_typed_availability_response_schema__when_slot_type_requested_with_mixed_case()`

### 6.4 단위 테스트 (UT)

#### UT-PQ-ZONE-01 일반 타입 총합 조회 서비스

- Given: 전체 Zone 목록과 일반 타입 집계 결과가 주어진다.
- When: 일반 타입 여석 조회 서비스를 호출한다.
- Then: 전체 Zone의 일반 타입 `available_count` 총합만 반환한다.
- 추천 메서드명: `should_return_total_available_count__when_general_slot_type_requested()`

#### UT-PQ-ZONE-02 전기차 타입 총합 조회 서비스

- Given: 전체 Zone 목록과 전기차 타입 집계 결과가 주어진다.
- When: 전기차 타입 여석 조회 서비스를 호출한다.
- Then: 전체 Zone의 전기차 타입 `available_count` 총합만 반환한다.
- 추천 메서드명: `should_return_total_available_count__when_ev_slot_type_requested()`

#### UT-PQ-ZONE-03 장애인 타입 총합 조회 서비스

- Given: 전체 Zone 목록과 장애인 타입 집계 결과가 주어진다.
- When: 장애인 타입 여석 조회 서비스를 호출한다.
- Then: 전체 Zone의 장애인 타입 `available_count` 총합만 반환한다.
- 추천 메서드명: `should_return_total_available_count__when_disabled_slot_type_requested()`

#### UT-PQ-ZONE-04 타입 검증

- Given: 지원하지 않는 `slot_type` 값이 전달된다.
- When: 조회 조건 검증을 수행한다.
- Then: 검증 오류를 발생시킨다.
- 추천 메서드명: `should_raise_validation_error__when_slot_type_is_unsupported()`

#### UT-PQ-ZONE-05 전체 타입 총합 조회 서비스

- Given: 전체 Zone 목록과 모든 지원 타입 집계 결과가 주어진다.
- When: `slot_type` 없이 여석 조회 서비스를 호출한다.
- Then: 전체 Zone의 전체 타입 `available_count` 총합만 반환한다.
- 추천 메서드명: `should_return_total_available_count_for_all_slot_types__when_slot_type_not_provided()`

#### UT-PQ-ZONE-06 데이터 없는 타입 0 반환 서비스

- Given: 지원하는 타입이지만 집계 결과가 비어 있다.
- When: 타입별 여석 조회 서비스를 호출한다.
- Then: `availableCount=0`을 반환한다.
- 추천 메서드명: `should_return_zero_available_count__when_supported_slot_type_has_no_projection()`

#### UT-PQ-ZONE-07 전체 조회 누락 타입 포함 합산 서비스

- Given: 전체 타입 집계 결과에서 일부 타입이 비어 있다.
- When: `slot_type` 없이 여석 조회 서비스를 호출한다.
- Then: 존재하는 집계만 합산한 전체 잔여석을 반환한다.
- 추천 메서드명: `should_return_total_available_count__when_some_slot_types_have_no_projection()`

#### UT-PQ-ZONE-09 입력 정규화 서비스

- Given: 지원하는 타입을 소문자 또는 혼합 대소문자로 전달한다.
- When: 타입별 여석 조회 서비스를 호출한다.
- Then: 표준 대문자 타입으로 정규화된 응답을 반환한다.
- 추천 메서드명: `should_return_normalized_slot_type__when_slot_type_requested_with_mixed_case()`

### 6.5 저장소/DB 테스트 (RT)

#### RT-PQ-ZONE-01 타입별 집계 조회

- Given: 전체 Zone의 타입별 집계 데이터가 저장되어 있다.
- When: 특정 타입의 전체 Zone 여석 조회용 쿼리를 실행한다.
- Then: 요청 타입에 해당하는 `available_count`를 합산할 수 있다.
- 추천 메서드명: `should_fetch_total_available_count_by_slot_type__when_repository_called()`

#### RT-PQ-ZONE-02 여석 불변식 제약

- Given: `available_count`가 음수이거나 `total_count - occupied_count`와 일치하지 않는 데이터를 저장하려 한다.
- When: `ZoneAvailability`를 저장한다.
- Then: 체크 제약 위반으로 실패한다.
- 추천 메서드명: `should_fail_when_zone_availability_invariant_is_broken__when_saving_projection()`

## 7. 이번 기능의 TDD 착수 순서

1. `AT-PQ-ZONE-01`부터 `AT-PQ-ZONE-05`까지 실패 테스트를 먼저 작성한다.
2. `CT-PQ-ZONE-01`부터 `CT-PQ-ZONE-05`까지 API 계약을 고정한다.
3. `UT-PQ-ZONE-01`부터 `UT-PQ-ZONE-05`까지 서비스/검증 로직을 고정한다.
4. 필요한 경우 `RT-PQ-ZONE-01`부터 `RT-PQ-ZONE-02`까지 저장소/DB 동작을 고정한다.
5. 그 다음 View, Serializer, Service, Repository 순으로 최소 구현을 추가한다.
