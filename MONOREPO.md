# AutoE 모노레포 골격

## 디렉토리 구조

- `services/` : 독립 배포 가능한 서비스
- `docs/architecture/` : 아키텍처 문서 및 ADR

## 서비스

- `parking-command-service` : 입차/출차 쓰기 모델
- `parking-query-service` : 조회 모델 및 프로젝션
- `vehicle-service` : 차량/차량 타입 소유
- `zone-service` : 존/슬롯 메타데이터 소유
- `orchestration-service` : 동기식 서비스 간 워크플로우 조정

## 원칙

- 서비스별 데이터베이스 분리
- 서비스 간 DB FK 금지
- 서비스 통신은 도메인 서버 구현 완료 후 연결
- 각 서비스는 마이그레이션/테스트를 독립 관리
- 모든 기능 개발은 TDD(RED -> GREEN -> REFACTOR) 준수
