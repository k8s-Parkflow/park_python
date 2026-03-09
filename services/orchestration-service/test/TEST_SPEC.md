# orchestration-service 테스트 명세 (연동 전 단계)

## 1. 목적

- 현재는 도메인 서버 통신 연결 전 단계이므로, 오케스트레이션 정책만 우선 검증한다.
- 실제 통신 연동 시작 시 계약 테스트와 통합 인수 테스트를 확장한다.

## 2. 인수 테스트 (AT)

### AT-OR-CORE-01 입차 오케스트레이션 순서
- Given: 하위 클라이언트(mock)가 정상 응답한다.
- When: 입차 오케스트레이션 실행.
- Then: 정의된 순서로 호출되고 통합 결과를 반환한다.
- 추천 메서드명: `test_execute_entry_flow_in_order()`

### AT-OR-CORE-02 실패 시 보상 정책
- Given: 중간 단계 클라이언트가 실패한다.
- When: 오케스트레이션 실행.
- Then: 보상 로직이 실행되고 실패 응답을 반환한다.
- 추천 메서드명: `test_run_compensation_on_mid_flow_failure()`

### AT-OR-CORE-03 멱등 재요청 처리
- Given: 동일 키 요청이 이미 성공 처리되었다.
- When: 동일 키 재호출.
- Then: 하위 호출 재실행 없이 기존 결과를 반환한다.
- 추천 메서드명: `test_return_cached_result_for_replayed_idempotency_key()`

## 3. 계약 테스트 (CT)

- 현재 단계: 서비스 통신 API 미연결로 실행 보류.
- 연동 시작 시 추가: 엔드포인트 스키마, 상태코드, 하위호환 게이트.

## 4. 단위 테스트 (UT)

### UT-OR-POLICY-01 재시도 정책
- Given: 재시도 가능/불가 오류.
- When: 정책 엔진 평가.
- Then: 재시도 가능한 오류만 지정 횟수 재시도한다.
- 추천 메서드명: `test_retry_only_retryable_errors()`

### UT-OR-POLICY-02 타임아웃 정책
- Given: 클라이언트 응답 지연.
- When: 호출 실행.
- Then: 타임아웃으로 실패 전환.
- 추천 메서드명: `test_fail_fast_on_dependency_timeout()`

### UT-OR-POLICY-03 서킷브레이커 정책
- Given: 연속 실패가 임계치 초과.
- When: 추가 요청 처리.
- Then: 즉시 차단된다.
- 추천 메서드명: `test_open_circuit_after_failure_threshold()`
