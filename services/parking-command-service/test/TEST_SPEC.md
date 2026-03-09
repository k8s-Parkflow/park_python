# parking-command-service 테스트 명세 (엔터티 빠른 고정)

## 1. 목적

- ERD 기반 엔터티(`PARKING_SLOT`, `SLOT_OCCUPANCY`, `PARKING_HISTORY`)를 빠르게 확정한다.
- AC는 핵심 흐름만 유지하고, 세부 분기는 UT/파라미터 테스트로 커버한다.

## 2. 인수 테스트 (AT)

### AT-PC-CORE-01 입차/출차 핵심 흐름
- Given: 활성 + 비점유 슬롯이 존재한다.
- When: 입차 후 같은 차량을 출차한다.
- Then: 입차 시 세션/점유가 생성되고, 출차 시 세션 종료 + 점유 해제가 된다.
- 추천 메서드명: `test_create_and_close_session_on_entry_exit()`

### AT-PC-CORE-02 입차 가드레일
- Given: `alreadyOccupied` 또는 `inactiveSlot` 또는 `alreadyHasActiveSession` 상태다.
- When: 입차 요청한다.
- Then: 요청은 거부되고 상태는 변경되지 않는다.
- 추천 메서드명: `test_reject_entry_when_precondition_invalid()`

### AT-PC-CORE-03 출차 가드레일
- Given: 차량의 활성 세션이 없다.
- When: 출차 요청한다.
- Then: 요청은 거부되고 상태는 변경되지 않는다.
- 추천 메서드명: `test_reject_exit_when_no_active_session()`

### AT-PC-CORE-04 동시성 보호
- Given: 동일 슬롯 대상 동시 입차 2건.
- When: 동시에 처리한다.
- Then: 정확히 1건만 성공한다.
- 추천 메서드명: `test_allow_only_one_entry_under_concurrency()`

## 3. 계약 테스트 (CT)

### CT-PC-CORE-01 커맨드 API 스키마
- Given: 필수 필드 누락/형식 오류 요청.
- When: `/parking/entry`, `/parking/exit` 호출.
- Then: 400과 표준 오류 포맷을 반환한다.
- 추천 메서드명: `test_return_400_for_invalid_command_schema()`

### CT-PC-CORE-02 상태 코드 계약
- Given: 도메인 충돌/미존재 조건.
- When: 입차/출차 호출.
- Then: 409(충돌), 404(미존재) 계약을 유지한다.
- 추천 메서드명: `test_preserve_status_codes_for_conflict_and_not_found()`

## 4. 단위 테스트 (UT)

### UT-PC-HIST-01 이력 상태 전이
- Given: 시작된 주차 이력.
- When: `exit()` 호출.
- Then: `PARKED -> EXITED`, `exit_at` 세팅.
- 추천 메서드명: `test_mark_history_exited_and_set_exit_at()`

### UT-PC-OCC-01 점유 상태 전이
- Given: 비점유 슬롯 점유 모델.
- When: `occupy()` 후 `release()` 호출.
- Then: 점유 필드가 세팅되고 해제 시 null/false로 복귀.
- 추천 메서드명: `test_set_and_clear_occupancy_fields()`

### UT-PC-SVC-01 입차 사전조건 검증
- Given: `alreadyOccupied | inactiveSlot | activeSessionExists` 상태.
- When: 엔트리 도메인 서비스 호출.
- Then: 예외를 발생시킨다.
- 추천 메서드명: `test_raise_error_when_entry_precondition_invalid()`

### UT-PC-SVC-02 시간값 갱신
- Given: 상태 변경 전 엔터티.
- When: 점유/해제/종료 전이가 일어난다.
- Then: `updated_at`이 갱신된다.
- 추천 메서드명: `test_update_timestamp_on_state_transition()`

## 5. 저장소/DB 제약 테스트 (RT)

### RT-PC-DB-01 활성 세션 유니크
- Given: 동일 차량의 `exit_at IS NULL` 세션 2건 저장 시도.
- When: 저장한다.
- Then: 2번째 저장이 실패한다.
- 추천 메서드명: `test_fail_second_active_session_for_same_vehicle()`

### RT-PC-DB-02 점유 체크 제약
- Given: `occupied=true`인데 세션/차량/시간 중 하나가 null.
- When: 저장한다.
- Then: 제약 위반으로 실패한다.
- 추천 메서드명: `test_fail_when_occupied_fields_missing()`
