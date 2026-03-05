# orchestration-service

동기식으로 여러 도메인 서비스를 조합해 워크플로우를 수행하는 조정 서비스.

## 책임

- 서비스 간 호출 순서 제어
- 재시도/타임아웃/서킷브레이커 정책 적용
- 멱등 키 처리
- 중간 실패 시 보상 로직 수행

## TDD 우선 개발 순서

1. `test/acceptance/` 실패 테스트 작성
2. `test/contract/` 실패 테스트 작성
3. `test/unit/` 실패 테스트 작성
4. `src/` 최소 구현
5. 테스트 통과 후 리팩터링

## 테스트 디렉토리

- `test/acceptance/` : 시나리오 테스트
- `test/contract/` : API 계약 테스트
- `test/unit/` : 정책/도메인 로직 테스트
