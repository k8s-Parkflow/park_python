# parking-command-service Zone/Slot 식별 방식 개선 TODO

## 목적

- 현재 입차/출차 API를 `slot_id` 단독 입력 구조에서 `slot_id + zone_id + slot_code` 동시 검증 구조로 재정의한다.
- 실제 운영 모델인 "하나의 Zone 안에 여러 Slot" 구조를 공개 API와 내부 구현에 일치시키기 위한 후속 작업을 정리한다.

## 배경

현재 구조에서는 `ParkingSlot`이 내부 PK인 `slot_id`를 갖고 있고, 입차 API도 사실상 이 값 중심으로 동작한다.

하지만 실제 주차장 도메인에서는 사용자가 인지하는 위치가 다음 구조에 더 가깝다.

- 하나의 Zone에 여러 Slot이 속한다.
- `slot_code`는 `A001` 같은 사람이 읽는 슬롯 표시값이다.
- `slot_code`는 `zone_id` 내부에서만 유일하다.
- 목표 운영 규모:
  - Zone `100개`
  - Zone당 Slot `100개`
  - 총 Slot `10,000개`

즉, 입차는 "차량이 `zone_id=1`의 `slot_code=A001`에 들어온다"는 의미로 표현되고, 동시에 내부 PK인 `slot_id`로도 같은 슬롯인지 다시 검증할 수 있어야 한다.

## 최종 계약 방향

### 입차 요청

- `vehicle_num`
- `zone_id`
- `slot_code`
- `slot_id`
- `entry_at`

```json
{
  "vehicle_num": "69가-3455",
  "zone_id": 1,
  "slot_code": "A001",
  "slot_id": 33,
  "entry_at": "2026-03-10T09:00:00+09:00"
}
```

### 출차 요청

- `vehicle_num`
- `zone_id`
- `slot_code`
- `slot_id`
- `exit_at`

```json
{
  "vehicle_num": "69가-3455",
  "zone_id": 1,
  "slot_code": "A001",
  "slot_id": 33,
  "exit_at": "2026-03-10T12:10:00+09:00"
}
```

### 성공 응답

- `history_id`
- `vehicle_num`
- `zone_id`
- `slot_code`
- `slot_id`
- `status`
- `entry_at`
- `exit_at`

```json
{
  "history_id": 101,
  "vehicle_num": "69가3455",
  "zone_id": 1,
  "slot_code": "A001",
  "slot_id": 33,
  "status": "PARKED",
  "entry_at": "2026-03-10T09:00:00+09:00",
  "exit_at": null
}
```

## 확정된 규칙

- `slot_code`는 컬럼명과 API 필드명 모두 `slot_code`로 유지한다.
- 코드 주석과 문서에는 `slot_code`가 실제로 `A001` 같은 슬롯 표시값이라는 의미를 남긴다.
- `slot_code`는 `zone_id` 내부에서만 유일하다.
- `slot_id`는 내부 PK 검증용 식별자로 유지한다.
- `slot_id`와 `zone_id + slot_code`는 같은 슬롯을 가리켜야 한다.
- `slot_id` 또는 `zone_id + slot_code` 둘 중 하나라도 존재하지 않으면 `404 not_found`다.
- `slot_id`와 `zone_id + slot_code`가 각각 존재하지만 서로 다른 슬롯을 가리키면 `400 bad_request`다.
- 출차는 `vehicle_num` 기준 활성 세션 1건을 찾는다.
- 출차 시 활성 세션은 있지만 요청한 `zone_id + slot_code + slot_id`가 현재 점유 위치와 다르면 `409 conflict`다.
- `slot_code`는 trim, uppercase 같은 정규화를 하지 않는다.
- 요청의 `slot_code`는 저장된 값과 정확히 일치해야 하며 `a001`과 `A001`을 같은 값으로 보정하지 않는다.
- 성공 응답에는 `zone_id`, `slot_code`, `slot_id`를 모두 포함한다.

## 현재 구조의 한계

### 1. 공개 API가 슬롯 위치 맥락을 충분히 표현하지 못함

- 현재 계약만 봐서는 차량이 어느 Zone의 어느 Slot에 들어갔는지 바로 드러나지 않는다.
- 운영자와 프론트는 `zone_id + slot_code`를 함께 받아야 위치를 명확하게 표현할 수 있다.

### 2. 내부 PK만으로는 업무 의미를 설명하기 어려움

- `slot_id=8457`은 사람이 읽기 어렵다.
- 반면 `zone_id=85`, `slot_code=A057`은 즉시 해석 가능하다.

### 3. 위치 식별값 교차 검증이 현재 계약에 없음

- 지금은 `slot_id`만 맞으면 처리되기 쉽다.
- 앞으로는 `slot_id`와 `zone_id + slot_code`가 모두 맞는지 교차 검증해야 잘못된 위치 요청을 초기에 차단할 수 있다.

## TODO

## Phase 1. 계약 재정의

- [ ] `TEST_SPEC_PARKING_RECORD_API.md`를 `slot_id + zone_id + slot_code` 기준으로 전면 수정
- [ ] Swagger/OpenAPI 문서의 입차/출차 request 및 response 스키마 수정
- [ ] 구현 문서와 커버리지 문서에서 기존 `slot_id` 단독 입력 전제를 제거
- [ ] 오류 계약을 `404 not_found`, `400 bad_request`, `409 conflict` 기준으로 고정

## Phase 2. DTO/Serializer 수정

- [ ] `EntryCommand`, `ExitCommand`에 `zone_id`, `slot_code`, `slot_id`를 모두 반영
- [ ] serializer에서 `zone_id` 정수 검증 추가
- [ ] serializer에서 `slot_code` 필수 문자열 검증 추가
- [ ] serializer에서 `slot_id` 정수 검증과 필수값 검증 유지
- [ ] `slot_code`에 대해 trim, uppercase 같은 정규화를 하지 않도록 명시
- [ ] 잘못된 `slot_code` 형식, 빈 값, 대소문자 불일치 입력에 대한 오류 계약 추가

## Phase 3. Repository 조회 방식 변경

- [ ] `slot_id` 조회와 `(zone_id, slot_code)` 조회를 함께 수행할 수 있는 저장소 API 정의
- [ ] 두 식별자가 같은 `ParkingSlot`을 가리키는지 검증하는 저장소 메서드 추가
- [ ] `slot_id` 미존재, `(zone_id, slot_code)` 미존재, 식별 불일치를 구분해 예외 매핑
- [ ] `(zone_id, slot_code)` 유니크 제약을 저장소 테스트로 다시 고정

## Phase 4. Service 로직 정리

- [ ] `create_entry()`가 `slot_id + zone_id + slot_code`를 함께 검증하도록 수정
- [ ] `complete_exit()`도 활성 세션 조회 후 요청 위치와 현재 점유 위치를 비교하도록 수정
- [ ] 출차 위치 충돌을 `409 conflict`로 매핑
- [ ] 반환 snapshot에 `zone_id`, `slot_code`, `slot_id`를 모두 포함하도록 확장
- [ ] 코드 주석에 `slot_code`가 슬롯 표시값이라는 설명 추가

## Phase 5. Projection/Query 연계 보강

- [ ] `CurrentParkingView` 갱신 시 `zone_id`, `slot_id` 연계가 새 계약과 충돌하지 않는지 점검
- [ ] 필요 시 projection에 `slot_code`를 추가할지 결정
- [ ] 출차 후 현재 위치 제거 로직이 요청 위치 검증과 모순되지 않는지 회귀 테스트 추가
- [ ] `ZoneAvailability` 집계가 새 입차 계약에서도 일관적인지 확인

## Phase 6. 테스트 전면 개편

- [ ] Acceptance
  - [ ] 입차/출차 성공 요청을 `slot_id + zone_id + slot_code` 기준으로 변경
  - [ ] `slot_id` 미존재 또는 `(zone_id, slot_code)` 미존재 케이스 추가
  - [ ] `slot_id`와 `(zone_id, slot_code)` 불일치 시 `400` 케이스 추가
  - [ ] 출차 위치 충돌 시 `409` 케이스 추가
- [ ] Contract
  - [ ] request schema에 `zone_id`, `slot_code`, `slot_id`를 모두 고정
  - [ ] response schema에 `zone_id`, `slot_code`, `slot_id`를 모두 고정
  - [ ] `slot_code` 정확 일치 검증 계약 추가
  - [ ] 새 오류 코드 계약 고정
- [ ] Unit
  - [ ] serializer `slot_code` 검증 테스트 추가
  - [ ] service가 슬롯 식별자 교차 검증을 수행하는지 검증
  - [ ] 출차 위치 충돌 예외 검증
  - [ ] snapshot 매핑 필드 확대 검증
- [ ] Repository
  - [ ] `(zone_id, slot_code)` 조회 테스트 추가
  - [ ] `slot_id`와 `(zone_id, slot_code)` 일치성 검증 테스트 추가
  - [ ] 서로 다른 Zone의 동일 `slot_code` 허용 확인
  - [ ] 같은 Zone의 중복 `slot_code` 차단 확인

## Phase 7. 데이터 준비/운영 고려

- [ ] Zone 100개, Zone당 Slot 100개 생성 전략 정리
- [ ] 총 10,000개 슬롯 생성용 seed 또는 fixture 전략 검토
- [ ] `slot_code` 표준 포맷을 운영 데이터 기준으로 고정
- [ ] 운영에서 `slot_code`가 변경 가능한지, 불변인지 정책 결정

## 추천 진행 순서

1. 테스트 명세서를 새 계약 기준으로 먼저 고정
2. serializer / DTO / service / repository 계약 변경
3. acceptance, contract, unit, repository 테스트 재작성
4. 구현 코드 GREEN 반영
5. projection / swagger / 커버리지 문서 동기화
