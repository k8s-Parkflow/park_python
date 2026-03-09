# parking-command-service Zone/Slot 식별 방식 개선 TODO

## 목적

- 현재 입차 API가 `slot_id`만 받는 구조를 `zone_id + slot_code` 기반으로 재정의한다.
- 실제 운영 모델인 "하나의 Zone 안에 여러 Slot" 구조를 공개 API와 내부 구현에 일치시키기 위한 후속 작업을 정리한다.

## 배경

현재 구조에서는 `PARKING_SLOT`가 내부 PK인 `slot_id`를 갖고 있고, 입차 API도 이 값을 직접 받는다.

하지만 실제 주차장 도메인에서는 사용자가 인지하는 위치가 다음 구조에 더 가깝다.

- 하나의 Zone에 여러 Slot이 속한다.
- Slot 코드는 Zone 내부에서만 유일하다.
- 예: `zone_id=1` 의 `A001`, `A002`, `A003` ...
- 목표 운영 규모:
  - Zone `100개`
  - Zone당 Slot `100개`
  - 총 Slot `10,000개`

즉, 입차는 "차량이 `zone_id=1` 의 `slot_code=A001` 에 들어온다"는 의미로 표현되는 것이 자연스럽다.

## 현재 구조의 한계

### 1. 공개 API가 내부 PK에 과도하게 의존함

- 현재 입차 요청은 `slot_id`를 직접 받는다.
- `slot_id`는 DB 내부 식별자일 뿐, 운영자나 외부 호출자가 직접 인지하기 쉬운 값이 아니다.

### 2. Zone 맥락이 요청 계약에 드러나지 않음

- 슬롯이 어떤 Zone에 속하는지 API 요청만 보고는 드러나지 않는다.
- `slot_id`를 아는 쪽은 결국 별도 조회나 내부 매핑을 알고 있어야 한다.

### 3. 슬롯 코드의 업무 의미가 API에 반영되지 않음

- 현재 데이터 모델에는 `(zone_id, slot_code)` 유니크 제약이 이미 있다.
- 그런데 공개 계약은 이 도메인 식별 방식을 활용하지 못하고 있다.

### 4. 대량 슬롯 운영 시 가독성과 운영성이 떨어짐

- 100개 존, 10,000개 슬롯 환경에서 `slot_id=8457` 같은 값은 의미 파악이 어렵다.
- 반면 `zone_id=85`, `slot_code=A057`은 사람이 바로 해석할 수 있다.

## 목표 방향

### 공개 API 식별자

입차 요청은 내부 PK가 아니라 아래 식별자를 받도록 변경한다.

- `zone_id`
- `slot_code`

예시:

```json
{
  "vehicle_num": "69가-3455",
  "zone_id": 1,
  "slot_code": "A001",
  "entry_at": "2026-03-10T09:00:00+09:00"
}
```

### 내부 저장 구조

- 내부 DB에서는 기존처럼 `slot_id`를 PK로 유지해도 된다.
- 단, service/repository 레벨에서는 `zone_id + slot_code`로 `ParkingSlot`을 조회한 뒤 내부 `slot_id`를 사용한다.

### 응답 방향

응답에는 최소한 아래 정보가 포함되어야 한다.

- `history_id`
- `vehicle_num`
- `slot_id`
- `zone_id`
- `slot_code`
- `status`
- `entry_at`
- `exit_at`

즉, 내부 식별자와 업무 식별자를 함께 반환해 write 결과 해석이 가능해야 한다.

## TODO

## Phase 1. 계약 재정의

- [ ] 입차 API request schema를 `slot_id` 중심에서 `zone_id + slot_code` 중심으로 변경
- [ ] Swagger/OpenAPI 문서의 입차 request/response 스키마 수정
- [ ] 테스트 명세서 `TEST_SPEC_PARKING_RECORD_API.md`를 새 계약 기준으로 개정
- [ ] 커버리지 문서, 구현 문서에서 `slot_id` 직접 입력 전제를 제거

## Phase 2. DTO/Serializer 수정

- [ ] `EntryCommand`에서 `slot_id` 대신 `zone_id`, `slot_code`를 받도록 수정
- [ ] serializer에서 `zone_id` 정수 검증 추가
- [ ] serializer에서 `slot_code` 필수 문자열 검증 추가
- [ ] `slot_code` 정규화 정책 결정
  - 후보: trim만 수행
  - 후보: trim + uppercase
- [ ] malformed/empty/whitespace-only `slot_code` 오류 계약 추가

## Phase 3. Repository 조회 방식 변경

- [ ] `get_slot_for_update(slot_id=...)`를 `get_slot_for_update(zone_id=..., slot_code=...)` 형태로 변경
- [ ] `ParkingSlot` 조회 시 `(zone_id, slot_code)` 유니크 제약을 기준으로 잠금 조회
- [ ] slot 조회 실패 메시지를 "존 내 슬롯이 존재하지 않습니다" 같은 계약으로 재검토

## Phase 4. Service 로직 정리

- [ ] `create_entry()`가 `zone_id + slot_code` 기준으로 슬롯을 조회하도록 수정
- [ ] 반환 snapshot에 `zone_id`, `slot_code`를 포함하도록 확장
- [ ] projection writer 호출 시도 기존과 동일하게 유지하되, projection 데이터에도 `zone_id` 맥락이 손실되지 않도록 검토

## Phase 5. Projection/Query 연계 보강

- [ ] `CurrentParkingView`는 이미 `zone_id`, `slot_id`를 가지므로 현재 구조와의 차이를 점검
- [ ] 필요 시 `slot_code`도 projection에 포함할지 결정
- [ ] 출차 후 현재 위치 제거 로직이 zone 기반 식별 변경과 충돌하지 않는지 확인
- [ ] `ZoneAvailability`는 `zone_id` 기준 집계이므로 입차 계약 변경 후에도 계산이 일관적인지 회귀 테스트 추가

## Phase 6. 테스트 전면 개편

- [ ] Acceptance
  - [ ] 입차 성공 요청을 `zone_id + slot_code` 기준으로 변경
  - [ ] 존재하지 않는 Zone/Slot 조합 거부 케이스 추가
  - [ ] 동일 `slot_code`라도 다른 Zone이면 별개 슬롯으로 처리되는 케이스 추가
- [ ] Contract
  - [ ] request schema에서 `slot_id` 제거
  - [ ] response schema에 `zone_id`, `slot_code` 추가
  - [ ] `slot_code` 타입/필수값 오류 계약 추가
- [ ] Unit
  - [ ] serializer `slot_code` 검증 테스트 추가
  - [ ] service가 `zone_id + slot_code`로 repository를 호출하는지 검증
  - [ ] snapshot 매핑 필드 확대 검증
- [ ] Repository
  - [ ] `(zone_id, slot_code)` 잠금 조회 테스트 추가
  - [ ] 서로 다른 Zone의 동일 `slot_code` 허용 확인
  - [ ] 같은 Zone의 중복 `slot_code` 차단 확인

## Phase 7. 데이터 준비/운영 고려

- [ ] 초기 데이터 또는 fixture 생성 전략 수립
  - [ ] Zone 100개 생성
  - [ ] Zone당 Slot 100개 생성
  - [ ] 총 10,000개 슬롯 생성
- [ ] slot_code 규칙 표준화
  - 예: `A001` ~ `A100`
- [ ] Zone별 슬롯 대량 생성 스크립트 필요 여부 검토
- [ ] 운영에서 slot_code 변경이 가능한지, 불변인지 정책 결정

## 권장 계약 변경안

### 입차 요청

```json
{
  "vehicle_num": "69가-3455",
  "zone_id": 1,
  "slot_code": "A001",
  "entry_at": "2026-03-10T09:00:00+09:00"
}
```

### 입차 응답

```json
{
  "history_id": 101,
  "vehicle_num": "69가3455",
  "slot_id": 33,
  "zone_id": 1,
  "slot_code": "A001",
  "status": "PARKED",
  "entry_at": "2026-03-10T09:00:00+09:00",
  "exit_at": null
}
```

### 출차 응답

```json
{
  "history_id": 101,
  "vehicle_num": "69가3455",
  "slot_id": 33,
  "zone_id": 1,
  "slot_code": "A001",
  "status": "EXITED",
  "entry_at": "2026-03-10T09:00:00+09:00",
  "exit_at": "2026-03-10T12:10:00+09:00"
}
```

## 결정이 필요한 항목

- [ ] 입차 request에서 `slot_id`를 완전히 제거할지
- [ ] response에는 `slot_id`를 유지할지
- [ ] `slot_code` 대소문자 정규화를 할지
- [ ] `zone_id + slot_code` 외에 `zone_code` 같은 별도 업무 식별자를 둘지
- [ ] query projection에도 `slot_code`를 저장할지

## 추천 진행 순서

1. 테스트 명세서부터 `zone_id + slot_code` 기준으로 수정
2. serializer / DTO / service / repository 계약 변경
3. acceptance, contract, unit, repository 테스트 재작성
4. projection / swagger / 구현 문서 동기화
5. 대량 fixture 및 운영 초기화 전략 정리
