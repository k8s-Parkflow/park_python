# 서비스

각 서비스 디렉토리는 독립적으로 개발/테스트/배포 가능해야 한다.

## 표준 하위 디렉토리

- `src/` : 애플리케이션 소스
- `test/` : 테스트 코드
- `migrations/` : 데이터베이스 마이그레이션

## 현재 서비스

- `parking-command-service`
- `parking-query-service`
- `vehicle-service`
- `zone-service`
- `orchestration-service`

## TDD 기본 규칙

기능 하나당 아래 순서를 따른다.

1. Acceptance 테스트
2. Contract 테스트
3. Unit 테스트
4. 최소 구현
5. 리팩터링
