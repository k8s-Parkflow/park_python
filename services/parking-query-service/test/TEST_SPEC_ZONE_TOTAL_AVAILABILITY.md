# 타입별 전체 Zone 여석 총합 조회 테스트 명세

## 1. 목적

- `parking-query-service`의 타입별 전체 Zone 여석 총합 조회 기능을 TDD 순서로 안전하게 유지한다.
- 기존 완료 범위와 회귀 테스트 기준을 기능 단위로 독립 관리한다.

## 2. 공통 도메인 가정

- 조회 대상 Zone은 등록된 전체 Zone이다.
- 타입별 잔여석은 `parking_query_service.ZoneAvailability.available_count`를 기준으로 계산한다.
- 타입별 전체 잔여석은 전체 Zone에 속한 동일 타입 `available_count` 합계다.
- `slot_type`가 비어 있으면 지원하는 전체 타입의 `available_count` 합계를 반환한다.
- 응답은 Zone별 상세 목록이 아니라 타입별 총합 한 건만 반환한다.
- 잘못된 타입 요청은 표준 에러 포맷의 `400 bad_request`를 반환한다.

## 3. 목표 계약 초안

### 3.1 타입별 전체 Zone 여석 총합 조회

- `GET /api/zones/availabilities?slot_type={GENERAL|EV|DISABLED}`

```json
{
  "slotType": "GENERAL",
  "availableCount": 12
}
```

### 3.2 오류 응답

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

### 3.3 전체 타입 총합 응답

```json
{
  "availableCount": 23
}
```

## 4. 진행 상태

### 완료된 AC

- `AC-PQ-ZONE-01` 전체 Zone 일반 타입 여석 총합 조회
- `AC-PQ-ZONE-02` 전체 Zone 전기차 타입 여석 총합 조회
- `AC-PQ-ZONE-03` 전체 Zone 장애인 타입 여석 총합 조회
- `AC-PQ-ZONE-04` 지원하지 않는 타입 예외 처리
- `AC-PQ-ZONE-05` 전체 타입 여석 총합 조회
- `AC-PQ-ZONE-06` 데이터 없는 타입 0 반환
- `AC-PQ-ZONE-07` 전체 조회 시 데이터 없는 타입 포함 합산
- `AC-PQ-ZONE-08` 음수 잔여석 불가
- `AC-PQ-ZONE-09` 입력 정규화 정책

### 완료된 테스트 코드

- `AT-PQ-ZONE-01`부터 `AT-PQ-ZONE-07`, `AT-PQ-ZONE-09`
- `CT-PQ-ZONE-01`부터 `CT-PQ-ZONE-07`, `CT-PQ-ZONE-09`
- `UT-PQ-ZONE-01`부터 `UT-PQ-ZONE-07`, `UT-PQ-ZONE-09`
- `RT-PQ-ZONE-01`
- `RT-PQ-ZONE-02`

## 5. Acceptance Criteria

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

## 6. 인수 테스트 (AT)

#### AT-PQ-ZONE-01 일반 타입 총합 조회

- 상태: 완료
- Given: 전체 Zone과 일반 타입 집계 데이터가 존재한다.
- When: `slot_type=GENERAL`로 조회를 요청한다.
- Then: 전체 Zone의 일반 타입 잔여석 총합을 반환한다.
- 추천 메서드명: `should_return_general_total__when_general_requested()`

#### AT-PQ-ZONE-02 전기차 타입 총합 조회

- 상태: 완료
- Given: 전체 Zone과 전기차 타입 집계 데이터가 존재한다.
- When: `slot_type=EV`로 조회를 요청한다.
- Then: 전체 Zone의 전기차 타입 잔여석 총합을 반환한다.
- 추천 메서드명: `should_return_ev_total__when_ev_requested()`

#### AT-PQ-ZONE-03 장애인 타입 총합 조회

- 상태: 완료
- Given: 전체 Zone과 장애인 타입 집계 데이터가 존재한다.
- When: `slot_type=DISABLED`로 조회를 요청한다.
- Then: 전체 Zone의 장애인 타입 잔여석 총합을 반환한다.
- 추천 메서드명: `should_return_disabled_total__when_disabled_requested()`

#### AT-PQ-ZONE-04 잘못된 타입 요청

- 상태: 완료
- Given: 지원하지 않는 `slot_type` 값을 전달한다.
- When: 조회를 요청한다.
- Then: 400과 표준 오류 응답을 반환한다.
- 추천 메서드명: `should_return_bad_request__when_slot_type_invalid()`

#### AT-PQ-ZONE-05 전체 타입 총합 조회

- 상태: 완료
- Given: 전체 Zone과 각 타입 집계 데이터가 존재한다.
- When: `slot_type` 없이 조회를 요청한다.
- Then: 전체 Zone의 전체 타입 잔여석 총합을 반환한다.
- 추천 메서드명: `should_return_total__when_slot_type_missing()`

#### AT-PQ-ZONE-06 데이터 없는 타입 0 반환

- 상태: 완료
- Given: 지원하는 타입이지만 집계 데이터가 하나도 없다.
- When: 해당 타입으로 조회를 요청한다.
- Then: `availableCount=0`을 반환한다.
- 추천 메서드명: `should_return_zero__when_projection_missing()`

#### AT-PQ-ZONE-07 전체 조회 시 누락 타입 포함 합산

- 상태: 완료
- Given: 전체 조회 대상 데이터 중 일부 타입 집계가 비어 있다.
- When: `slot_type` 없이 조회를 요청한다.
- Then: 존재하는 타입만 합산한 전체 잔여석을 반환한다.
- 추천 메서드명: `should_return_total__when_some_types_missing()`

#### AT-PQ-ZONE-09 입력 정규화

- 상태: 완료
- Given: 지원하는 타입을 소문자 또는 혼합 대소문자로 전달한다.
- When: 조회를 요청한다.
- Then: 표준 대문자 타입으로 정규화되어 정상 응답을 반환한다.
- 추천 메서드명: `should_normalize_slot_type__when_mixed_case()`

## 7. 계약 테스트 (CT)

#### CT-PQ-ZONE-01 일반 타입 총합 응답 스키마

- 상태: 완료
- Given: 일반 타입 총합 조회가 가능한 데이터가 있다.
- When: `GET /api/zones/availabilities?slot_type=GENERAL`를 호출한다.
- Then: `slotType`, `availableCount` 필드와 각 필드 타입 계약을 만족한다.
- 추천 메서드명: `should_match_typed_total_schema__when_general_requested()`

#### CT-PQ-ZONE-02 전기차 타입 총합 응답 스키마

- 상태: 완료
- Given: 전기차 타입 총합 조회가 가능한 데이터가 있다.
- When: `GET /api/zones/availabilities?slot_type=EV`를 호출한다.
- Then: `slotType`, `availableCount` 필드와 각 필드 타입 계약을 만족한다.
- 추천 메서드명: `should_match_typed_total_schema__when_ev_requested()`

#### CT-PQ-ZONE-03 장애인 타입 총합 응답 스키마

- 상태: 완료
- Given: 장애인 타입 총합 조회가 가능한 데이터가 있다.
- When: `GET /api/zones/availabilities?slot_type=DISABLED`를 호출한다.
- Then: `slotType`, `availableCount` 필드와 각 필드 타입 계약을 만족한다.
- 추천 메서드명: `should_match_typed_total_schema__when_disabled_requested()`

#### CT-PQ-ZONE-04 오류 응답 계약

- 상태: 완료
- Given: 지원하지 않는 `slot_type`로 요청한다.
- When: `GET /api/zones/availabilities?slot_type=VIP`를 호출한다.
- Then: 400과 표준 오류 응답 포맷을 유지한다.
- 추천 메서드명: `should_preserve_bad_request__when_slot_type_invalid()`

#### CT-PQ-ZONE-05 전체 타입 총합 응답 스키마

- 상태: 완료
- Given: 전체 타입 총합 조회가 가능한 데이터가 있다.
- When: `GET /api/zones/availabilities`를 호출한다.
- Then: `availableCount` 필드만 가지는 응답 계약을 만족한다.
- 추천 메서드명: `should_match_total_schema__when_slot_type_missing()`

#### CT-PQ-ZONE-06 데이터 없는 타입 0 응답 스키마

- 상태: 완료
- Given: 지원하는 타입이지만 집계 데이터가 없다.
- When: 해당 타입으로 조회를 요청한다.
- Then: 정상 응답과 기존 타입별 스키마 계약을 유지한다.
- 추천 메서드명: `should_match_typed_total_schema__when_projection_missing()`

#### CT-PQ-ZONE-07 전체 조회 누락 타입 응답 스키마

- 상태: 완료
- Given: 일부 타입 집계가 비어 있다.
- When: `GET /api/zones/availabilities`를 호출한다.
- Then: `availableCount` 단일 필드 응답 계약을 유지한다.
- 추천 메서드명: `should_match_total_schema__when_some_types_missing()`

#### CT-PQ-ZONE-09 입력 정규화 응답 스키마

- 상태: 완료
- Given: 지원하는 타입을 대소문자가 섞인 값으로 전달한다.
- When: 조회를 요청한다.
- Then: 응답은 정상 타입별 스키마를 유지하고 `slotType`은 표준 대문자다.
- 추천 메서드명: `should_match_typed_total_schema__when_slot_type_normalized()`

## 8. 단위 테스트 (UT)

#### UT-PQ-ZONE-01 일반 타입 총합 조회 서비스

- 상태: 완료
- Given: 전체 Zone 목록과 일반 타입 집계 결과가 주어진다.
- When: 일반 타입 여석 조회 서비스를 호출한다.
- Then: 전체 Zone의 일반 타입 `available_count` 총합만 반환한다.
- 추천 메서드명: `should_return_general_total__when_general_requested()`

#### UT-PQ-ZONE-02 전기차 타입 총합 조회 서비스

- 상태: 완료
- Given: 전체 Zone 목록과 전기차 타입 집계 결과가 주어진다.
- When: 전기차 타입 여석 조회 서비스를 호출한다.
- Then: 전체 Zone의 전기차 타입 `available_count` 총합만 반환한다.
- 추천 메서드명: `should_return_ev_total__when_ev_requested()`

#### UT-PQ-ZONE-03 장애인 타입 총합 조회 서비스

- 상태: 완료
- Given: 전체 Zone 목록과 장애인 타입 집계 결과가 주어진다.
- When: 장애인 타입 여석 조회 서비스를 호출한다.
- Then: 전체 Zone의 장애인 타입 `available_count` 총합만 반환한다.
- 추천 메서드명: `should_return_disabled_total__when_disabled_requested()`

#### UT-PQ-ZONE-04 타입 검증

- 상태: 완료
- Given: 지원하지 않는 `slot_type` 값이 전달된다.
- When: 조회 조건 검증을 수행한다.
- Then: 검증 오류를 발생시킨다.
- 추천 메서드명: `should_raise_validation_error__when_slot_type_invalid()`

#### UT-PQ-ZONE-05 전체 타입 총합 조회 서비스

- 상태: 완료
- Given: 전체 Zone 목록과 모든 지원 타입 집계 결과가 주어진다.
- When: `slot_type` 없이 여석 조회 서비스를 호출한다.
- Then: 전체 Zone의 전체 타입 `available_count` 총합만 반환한다.
- 추천 메서드명: `should_return_total__when_slot_type_missing()`

#### UT-PQ-ZONE-06 데이터 없는 타입 0 반환 서비스

- 상태: 완료
- Given: 지원하는 타입이지만 집계 결과가 비어 있다.
- When: 타입별 여석 조회 서비스를 호출한다.
- Then: `availableCount=0`을 반환한다.
- 추천 메서드명: `should_return_zero__when_projection_missing()`

#### UT-PQ-ZONE-07 전체 조회 누락 타입 포함 합산 서비스

- 상태: 완료
- Given: 전체 타입 집계 결과에서 일부 타입이 비어 있다.
- When: `slot_type` 없이 여석 조회 서비스를 호출한다.
- Then: 존재하는 집계만 합산한 전체 잔여석을 반환한다.
- 추천 메서드명: `should_return_total__when_some_types_missing()`

#### UT-PQ-ZONE-09 입력 정규화 서비스

- 상태: 완료
- Given: 지원하는 타입을 소문자 또는 혼합 대소문자로 전달한다.
- When: 타입별 여석 조회 서비스를 호출한다.
- Then: 표준 대문자 타입으로 정규화된 응답을 반환한다.
- 추천 메서드명: `should_normalize_slot_type__when_mixed_case()`

## 9. 저장소/DB 테스트 (RT)

#### RT-PQ-ZONE-01 타입별 집계 조회

- 상태: 완료
- Given: 전체 Zone의 타입별 집계 데이터가 저장되어 있다.
- When: 특정 타입의 전체 Zone 여석 조회용 쿼리를 실행한다.
- Then: 요청 타입에 해당하는 `available_count`를 합산할 수 있다.
- 추천 메서드명: `should_fetch_total_by_slot_type__when_queried()`

#### RT-PQ-ZONE-02 여석 불변식 제약

- 상태: 완료
- Given: `available_count`가 음수이거나 `total_count - occupied_count`와 일치하지 않는 데이터를 저장하려 한다.
- When: `ZoneAvailability`를 저장한다.
- Then: 체크 제약 위반으로 실패한다.
- 추천 메서드명: `should_fail_invariant__when_saving_invalid_availability()`

## 10. 회귀 기준

- 이후 신규 AC가 추가되면 이 기능 문서 안에서 `AT -> CT -> UT -> RT -> 최소 구현 -> 리팩터링` 순서를 유지한다.
- 현재 완료 범위는 회귀 테스트 대상으로 유지한다.
