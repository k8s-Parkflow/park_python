# 차량 번호 기반 현재 위치 조회 테스트 명세

## 1. 목적

- 차량 번호로 현재 차량의 위치를 조회하는 기능을 TDD 순서로 안전하게 개발한다.
- 정상 조회, 입력 정규화, 오류 분기, 최신 프로젝션 우선 정책을 명확히 고정한다.

## 2. 공통 도메인 가정

- 현재 위치의 조회 기준은 `parking_query_service.CurrentParkingView.vehicle_num`이다.
- 현재 위치 응답의 `zone_name`, `slot_name`은 `CurrentParkingView`에 저장된 사용자 조회용 projection 값이다.
- 한 차량 번호에 대한 활성 현재 위치는 최대 1건만 유지한다.
- 차량 번호 조회 입력은 비교 전에 하이픈과 공백을 제거하는 방식으로 정규화한다.
- 정규화 후 차량이 등록되어 있으나 현재 위치 프로젝션이 없으면 표준 에러 포맷의 `404 not_found`를 반환한다.
- 정규화 후 차량 자체가 등록되어 있지 않으면 표준 에러 포맷의 `404 not_found`를 반환한다.
- 잘못된 차량 번호 형식은 표준 에러 포맷의 `400 bad_request`를 반환한다.

## 3. 목표 계약 초안

### 3.1 현재 위치 조회

- `GET /api/parking/current/{vehicle_num}`

```json
{
  "vehicle_num": "69가-3455",
  "zone_name": "A존",
  "slot_name": "A033"
}
```

### 3.2 현재 주차 중이 아닌 차량 응답

```json
{
  "error": {
    "code": "not_found",
    "message": "현재 주차 중인 차량이 없습니다."
  }
}
```

### 3.3 미등록 차량 응답

```json
{
  "error": {
    "code": "not_found",
    "message": "존재하지 않는 차량입니다."
  }
}
```

## 4. Acceptance Criteria

#### AC-PQ-LOC-01 현재 주차 중 차량 위치 조회 성공

- 사용자가 차량 번호를 입력하면 현재 주차 중인 차량의 위치를 조회할 수 있다.
- 예를 들어 `69가-3455`가 현재 `A존`의 `A033` 슬롯에 있으면 `A존 / A033`을 반환한다.

#### AC-PQ-LOC-02 위치 응답 필드 보장

- 정상 응답에는 `vehicle_num`, `zone_name`, `slot_name`이 포함되어야 한다.
- `zone_name`은 사용자 표시용 존 이름이고, `slot_name`은 사용자 표시용 슬롯 이름이어야 한다.

#### AC-PQ-LOC-03 차량 번호 입력 정규화

- 조회 입력은 하이픈과 공백 유무 차이를 허용해야 한다.
- 정규화 후 동일 차량 번호로 판단되면 동일한 현재 위치를 반환해야 한다.

#### AC-PQ-LOC-04 차량 번호 형식 검증

- 빈 문자열 또는 지원하지 않는 차량 번호 형식은 조회할 수 없어야 한다.
- 잘못된 입력이면 `400 bad_request`와 표준 오류 포맷을 반환해야 한다.

#### AC-PQ-LOC-05 현재 주차 중이 아닌 등록 차량 처리

- 등록된 차량이라도 활성 현재 위치가 없으면 위치를 반환하지 않아야 한다.
- 이 경우 `404 not_found`와 “현재 주차 중인 차량이 없습니다.” 메시지를 반환해야 한다.

#### AC-PQ-LOC-06 미등록 차량 처리

- 시스템에 등록되지 않은 차량 번호는 위치를 반환하지 않아야 한다.
- 이 경우 `404 not_found`와 “존재하지 않는 차량입니다.” 메시지를 반환해야 한다.

#### AC-PQ-LOC-07 최신 프로젝션 우선

- 동일 차량에 대해 최신 상태와 과거 상태가 경쟁하면 최신 `updated_at` 기준 데이터만 조회되어야 한다.
- 과거 이벤트나 오래된 반영 데이터가 최신 위치를 덮어쓰면 안 된다.

#### AC-PQ-LOC-08 활성 위치 단건성

- 한 차량 번호에 대한 활성 현재 위치는 최대 1건만 유지되어야 한다.
- 중복 활성 위치는 프로젝션 갱신 정책 또는 저장소/DB 제약으로 차단되어야 한다.

## 5. 인수 테스트 (AT)

#### AT-PQ-LOC-01 현재 주차 중 차량 위치 조회 성공

- Given: 등록된 차량 `69가-3455`가 현재 `A존`의 `A033` 슬롯에 주차 중이다.
- When: `GET /api/parking/current/69가-3455`를 호출한다.
- Then: `vehicle_num`, `zone_name=A존`, `slot_name=A033`을 반환한다.
- 추천 메서드명: `should_return_location__when_vehicle_parked()`

#### AT-PQ-LOC-02 차량 번호 입력 정규화

- Given: 등록된 차량 `69가-3455`의 현재 위치가 존재한다.
- When: 하이픈 또는 공백이 다른 형식의 차량 번호로 현재 위치를 조회한다.
- Then: 동일 차량으로 정규화되어 같은 위치를 반환한다.
- 추천 메서드명: `should_return_location__when_vehicle_num_normalized()`

#### AT-PQ-LOC-03 차량 번호 형식 오류

- Given: 빈 문자열 또는 지원하지 않는 형식의 차량 번호를 전달한다.
- When: 현재 위치를 조회한다.
- Then: `400 bad_request`와 표준 오류 응답을 반환한다.
- 추천 메서드명: `should_return_bad_request__when_vehicle_num_invalid()`

#### AT-PQ-LOC-04 현재 주차 중이 아닌 등록 차량 조회

- Given: 등록된 차량이지만 활성 현재 위치 프로젝션이 없다.
- When: 현재 위치를 조회한다.
- Then: `404 not_found`와 “현재 주차 중인 차량이 없습니다.”를 반환한다.
- 추천 메서드명: `should_return_not_found__when_vehicle_not_parked()`

#### AT-PQ-LOC-05 미등록 차량 조회

- Given: 시스템에 등록되지 않은 차량 번호다.
- When: 현재 위치를 조회한다.
- Then: `404 not_found`와 “존재하지 않는 차량입니다.”를 반환한다.
- 추천 메서드명: `should_return_not_found__when_vehicle_missing()`

#### AT-PQ-LOC-06 최신 프로젝션 반영

- Given: 동일 차량에 대해 과거 위치와 최신 위치 반영 이력이 존재한다.
- When: 현재 위치를 조회한다.
- Then: 최신 `updated_at` 기준의 `zone_name`, `slot_name`만 반환한다.
- 추천 메서드명: `should_return_latest_location__when_location_updated()`

## 6. 계약 테스트 (CT)

#### CT-PQ-LOC-01 현재 위치 조회 응답 스키마

- Given: 정상 조회가 가능한 현재 위치 데이터가 있다.
- When: `GET /api/parking/current/{vehicle_num}`를 호출한다.
- Then: `vehicle_num`, `zone_name`, `slot_name` 필수 필드와 타입 계약을 만족한다.
- 추천 메서드명: `should_match_location_schema__when_found()`

#### CT-PQ-LOC-02 차량 번호 형식 오류 응답 계약

- Given: 잘못된 차량 번호 형식으로 조회한다.
- When: `GET /api/parking/current/{vehicle_num}`를 호출한다.
- Then: `400 bad_request`와 표준 오류 응답 포맷을 유지한다.
- 추천 메서드명: `should_preserve_bad_request__when_vehicle_num_invalid()`

#### CT-PQ-LOC-03 현재 주차 중이 아닌 차량 오류 응답 계약

- Given: 등록된 차량이지만 현재 위치가 없다.
- When: `GET /api/parking/current/{vehicle_num}`를 호출한다.
- Then: `404 not_found`와 메시지 계약을 유지한다.
- 추천 메서드명: `should_preserve_not_found__when_vehicle_not_parked()`

#### CT-PQ-LOC-04 미등록 차량 오류 응답 계약

- Given: 등록되지 않은 차량 번호로 조회한다.
- When: `GET /api/parking/current/{vehicle_num}`를 호출한다.
- Then: `404 not_found`와 메시지 계약을 유지한다.
- 추천 메서드명: `should_preserve_not_found__when_vehicle_missing()`

#### CT-PQ-LOC-05 정규화 입력 성공 응답 계약

- Given: 현재 위치가 있는 차량을 하이픈 또는 공백 변형 값으로 조회한다.
- When: `GET /api/parking/current/{vehicle_num}`를 호출한다.
- Then: 정상 조회 응답 스키마를 유지한다.
- 추천 메서드명: `should_match_location_schema__when_vehicle_num_normalized()`

## 7. 단위 테스트 (UT)

#### UT-PQ-LOC-01 차량 번호 정규화

- Given: 하이픈과 공백이 포함된 차량 번호 입력이다.
- When: 조회용 차량 번호 정규화를 수행한다.
- Then: 비교 가능한 표준 값으로 변환된다.
- 추천 메서드명: `should_normalize_vehicle_num__when_formatted()`

#### UT-PQ-LOC-02 현재 위치 조회 서비스 조합

- Given: 현재 위치 프로젝션과 존/슬롯 마스터 데이터가 존재한다.
- When: 현재 위치 조회 서비스를 호출한다.
- Then: `zone_name`, `slot_name`을 포함한 응답 DTO를 반환한다.
- 추천 메서드명: `should_build_location__when_projection_found()`

#### UT-PQ-LOC-03 현재 주차 중이 아닌 등록 차량 예외

- Given: 차량은 등록되어 있지만 현재 위치 프로젝션이 없다.
- When: 현재 위치 조회 서비스를 호출한다.
- Then: 현재 주차 중이 아님 예외를 발생시킨다.
- 추천 메서드명: `should_raise_not_parked__when_location_missing()`

#### UT-PQ-LOC-04 미등록 차량 예외

- Given: 정규화된 차량 번호가 차량 마스터에 없다.
- When: 현재 위치 조회 서비스를 호출한다.
- Then: 차량 미등록 예외를 발생시킨다.
- 추천 메서드명: `should_raise_vehicle_not_found__when_vehicle_missing()`

#### UT-PQ-LOC-05 현재 위치 upsert 및 삭제

- Given: 동일 차량 데이터가 반복 반영되고 이후 출차 이벤트가 반영된다.
- When: 현재 위치 프로젝션 갱신 로직을 적용한다.
- Then: 최신 상태로 upsert되고 출차 시 제거된다.
- 추천 메서드명: `should_sync_location_projection__when_projection_applied()`

#### UT-PQ-LOC-06 시간 역전 보호

- Given: 최신 데이터 이후에 과거 타임스탬프 업데이트가 들어온다.
- When: 현재 위치 프로젝션 갱신 로직을 적용한다.
- Then: 현재 최신 상태를 과거 데이터가 덮어쓰지 못한다.
- 추천 메서드명: `should_ignore_stale_update__when_event_older()`

## 8. 저장소/DB 테스트 (RT)

#### RT-PQ-LOC-01 현재 위치 PK 제약

- Given: 동일 `vehicle_num`의 현재 위치 데이터가 중복 저장된다.
- When: 저장을 시도한다.
- Then: PK 제약으로 실패한다.
- 추천 메서드명: `should_fail_on_duplicate_vehicle_num__when_saving_location()`

#### RT-PQ-LOC-02 현재 위치 projection 조회

- Given: 현재 위치 프로젝션이 저장되어 있다.
- When: 차량 번호 기준 현재 위치 조회용 쿼리를 실행한다.
- Then: `zone_name`, `slot_name`을 함께 조회할 수 있다.
- 추천 메서드명: `should_fetch_location__when_vehicle_num_given()`

#### RT-PQ-LOC-03 현재 위치 미존재 조회 결과

- Given: 차량은 등록되어 있지만 현재 위치 프로젝션 행이 없다.
- When: 차량 번호 기준 현재 위치 조회용 쿼리를 실행한다.
- Then: 조회 결과가 비어 있어 서비스 계층이 404 분기로 처리할 수 있다.
- 추천 메서드명: `should_return_empty__when_location_missing()`

## 9. 이번 기능의 TDD 착수 순서

1. `AT-PQ-LOC-01`부터 `AT-PQ-LOC-06`까지 먼저 실패하는 인수 테스트를 작성한다.
2. 이후 `CT-PQ-LOC-01`부터 `CT-PQ-LOC-05`, `UT-PQ-LOC-01`부터 `UT-PQ-LOC-06`, `RT-PQ-LOC-01`부터 `RT-PQ-LOC-03` 순서로 확장한다.
3. 프로덕션 코드는 `AT -> CT -> UT -> RT` 실패 확인 이후 최소 구현으로 통과시키고 마지막에 리팩터링한다.
