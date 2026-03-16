# SQLite3 -> MariaDB 전환 범위 문서

## 구현 상태

- 2026-03-16 기준으로 본 문서의 전환 작업은 코드에 반영되었다.
- 현재 표준 드라이버는 `mysqlclient`다.
- 서비스별 database 분리 전략을 유지했다.
- 테스트도 SQLite 파일이 아니라 MariaDB 테스트 database 이름 전략으로 전환했다.
- 서비스 실행 스크립트와 Dockerfile도 MariaDB 계약으로 정리했다.

## 목적

- 현재 프로젝트가 실제 코드에서는 `sqlite3` 기반으로 묶여 있는 부분을 정리한다.
- 운영 프로덕션 환경을 `MariaDB` 기준으로 전환할 때 함께 수정해야 하는 범위를 문서화한다.
- 이 문서는 원래 구현 전 범위 확정 문서였고, 현재는 실제 반영 결과를 함께 기록한다.

## 확정된 결정

- Python 드라이버: `mysqlclient`
- DB 분리 방식: 서비스별 database 분리 유지
- 기본 DB 이름:
  - `autoe_orchestration`
  - `autoe_vehicle`
  - `autoe_zone`
  - `autoe_parking_command`
  - `autoe_parking_query`
- 공통 기본 연결값:
  - `HOST=127.0.0.1`
  - `PORT=3306`
  - `USER=root`
  - `PASSWORD=""`
- 테스트 DB 이름 전략:
  - `test_<alias>_<database_name>`

## 현재 상태 요약

프로젝트 README는 데이터베이스를 `MariaDB`로 설명하고 있지만, 실제 Django 설정과 테스트 구성은 `sqlite3` 기준으로 구현되어 있다.

확인된 현재 상태:

- 공용 DB 설정 모듈이 `sqlite3` 엔진을 반환한다.
- 루트 Django 앱과 각 서비스별 Django settings가 모두 `sqlite3` 빌더를 사용한다.
- 테스트 설정이 파일 기반 SQLite 테스트 DB 경로를 직접 생성한다.
- 서비스별 Dockerfile 주석과 권한 처리도 SQLite 파일 생성을 전제로 작성되어 있다.
- 루트 Dockerfile은 MySQL 계열 client 라이브러리 설치 흔적이 있으나, Python DB 드라이버 의존성은 정리되어 있지 않다.

## 전환 원칙

- 운영 환경의 표준 DB는 `MariaDB`로 고정한다.
- DB 전환은 단순 `ENGINE` 교체가 아니라, 설정, 드라이버, 컨테이너 빌드, 테스트 전략, 운영 환경변수, 문서의 일관성까지 함께 맞춘다.
- 서비스별 DB alias 구조는 유지하되, 각 alias가 SQLite 파일이 아니라 MariaDB 연결 정보를 사용하도록 전환한다.
- 구현은 이후 단계에서 진행하고, 이번 문서는 영향 범위와 변경 대상을 확정하는 데 목적이 있다.

## 전환 범위

### 1. 공용 DB 설정 계층

현재 확인 파일:

- `shared/database_config.py`
- `park_py/database_config.py`

현재 문제:

- `build_sqlite_database()`가 `django.db.backends.sqlite3`를 고정 반환한다.
- 서비스별 기본 DB 값이 `*.sqlite3` 파일명 중심으로 구성되어 있다.
- 환경변수도 사실상 SQLite 파일 경로 override 용도로만 설계되어 있다.

전환 범위:

- 공용 DB 빌더를 MariaDB 연결 정보 기반으로 재설계
- 서비스 alias별 DB 이름/호스트/포트/유저/비밀번호/env key 체계 재정의
- 서비스별 분리 DB를 유지할지, 하나의 MariaDB 인스턴스 안에서 스키마/DB를 분리할지 명시
- `CONN_MAX_AGE`, `OPTIONS`, `CHARSET`, `TEST` 설정 방식 검토

### 2. Django settings 계층

현재 확인 파일:

- `park_py/settings.py`
- `services/orchestration-service/src/orchestration_service/settings.py`
- `services/parking-command-service/src/parking_command_service/settings.py`
- `services/parking-query-service/src/parking_query_service/settings.py`
- `services/zone-service/src/zone_service/settings.py`
- `services/vehicle-service/src/vehicle_service/settings.py`

현재 문제:

- 루트 앱과 각 개별 서비스가 모두 SQLite 전용 빌더를 사용한다.
- 서비스별 기본값이 `BASE_DIR / "*.sqlite3"` 파일 경로다.

전환 범위:

- 각 settings가 MariaDB 공용 설정 빌더를 사용하도록 정리
- 운영 환경변수 기준 연결 구성으로 전환
- 서비스 단독 실행과 루트 통합 실행 양쪽 모두 같은 DB 계약을 따르도록 정리
- 개발/테스트/운영 설정 분리가 필요하면 settings 계층에서 명시

### 3. 테스트 설정 계층

현재 확인 파일:

- `park_py/settings_test.py`
- `park_py/settings_msa_test.py`
- `park_py/tests/multi_db/unit/test_ut_msa_database_config.py`
- `park_py/tests/multi_db/acceptance/test_at_msa_database_aliases.py`

영향 가능 파일:

- `park_py/tests/runtime/repository/test_rt_orchestration_http_runtime_settings.py`
- `park_py/tests/runtime/repository/test_rt_command_query_http_runtime_settings.py`
- `park_py/tests/runtime/repository/test_rt_internal_service_http_runtime_settings.py`

현재 문제:

- 테스트 DB가 `/tmp/autoE-test-dbs`, `.test_dbs` 아래 SQLite 파일명으로 생성된다.
- 단위 테스트가 `vehicle.sqlite3`, `parking_query.sqlite3` 같은 파일명을 직접 기대한다.

전환 범위:

- 테스트용 MariaDB DB 이름 생성 전략 정의
- 서비스 alias별 테스트 DB 격리 방식 정의
- 설정 테스트를 SQLite 파일명 검증에서 MariaDB 연결 계약 검증으로 변경
- 로컬/CI에서 테스트용 DB 준비 방식 문서화

### 4. Python 의존성 계층

현재 확인 파일:

- `requirements.txt`

현재 문제:

- Django는 MySQL/MariaDB backend를 사용할 수 있지만, 현재 requirements에는 DB 드라이버가 없다.
- Dockerfile 주석은 `mysqlclient 제외`라고 되어 있으나 실제 설치 대상이 명확하지 않다.

전환 범위:

- MariaDB 연결용 Python 드라이버를 프로젝트 표준으로 확정
- 선택한 드라이버 기준으로 `requirements.txt` 정리
- 드라이버에 필요한 OS 패키지와 Python 패키지의 조합을 문서화

결정 필요:

- `mysqlclient` 기반으로 갈지
- `mariadb` Python connector 기반으로 갈지
- 또는 다른 표준 드라이버를 사용할지

주의:

- 이 결정이 Dockerfile, CI 이미지, 로컬 개발 환경까지 연쇄적으로 영향을 준다.

### 5. Docker / 컨테이너 빌드 계층

현재 확인 파일:

- `Dockerfile`
- `services/orchestration-service/Dockerfile`
- `services/parking-command-service/Dockerfile`
- `services/parking-query-service/Dockerfile`
- `services/zone-service/Dockerfile`
- `services/vehicle-service/Dockerfile`

현재 문제:

- 일부 Dockerfile은 SQLite 전용이라는 설명을 포함한다.
- 일부는 `mysqlclient` 제외라는 주석을 가지지만, 실제 표준 드라이버가 정의되어 있지 않다.
- 일부는 SQLite DB 파일 쓰기 권한을 전제로 `chmod -R 777 /app`를 수행한다.

전환 범위:

- 선택한 MariaDB 드라이버에 필요한 OS 패키지 설치로 통일
- SQLite 파일 쓰기 전제 주석 제거
- DB 파일 생성 목적의 광범위 권한 부여 제거 가능 여부 검토
- 각 서비스 컨테이너가 MariaDB 접속 환경변수를 사용하도록 실행 계약 정리

### 6. 실행/마이그레이션 스크립트 계층

현재 확인 파일:

- `scripts/services/orchestration/migrate.sh`
- `scripts/services/parking-command/migrate.sh`
- `scripts/services/parking-query/migrate.sh`
- `scripts/services/zone/migrate.sh`
- `scripts/services/vehicle/migrate.sh`

현재 상태:

- 스크립트 자체는 Django `migrate` 호출 중심이라 직접적으로 SQLite에 묶여 있지는 않다.
- 다만 실제 동작은 settings의 DB 계약에 의존하므로, 환경변수 계약이 바뀌면 함께 맞춰야 한다.

전환 범위:

- 스크립트가 요구하는 MariaDB 환경변수 문서화
- 서비스 시작 전 DB readiness 보장이 필요한지 검토
- 운영 배포 시 migrate 순서와 대상 DB alias 정리

### 7. 운영 환경변수 / 배포 계약 계층

현재 상태:

- 현재 DB 환경변수는 주로 `*_DB_NAME` 하나로 SQLite 경로 override에 가깝다.

전환 범위:

- 서비스별 MariaDB 연결 환경변수 체계 정의
- 공통 prefix를 쓸지, 서비스별 prefix를 쓸지 규칙 확정
- 예시:
  - `ORCHESTRATION_DB_NAME`
  - `ORCHESTRATION_DB_HOST`
  - `ORCHESTRATION_DB_PORT`
  - `ORCHESTRATION_DB_USER`
  - `ORCHESTRATION_DB_PASSWORD`
- 동일하게 `VEHICLE`, `ZONE`, `PARKING_COMMAND`, `PARKING_QUERY`도 정의

추가 검토:

- 운영에서 DB별 계정 분리 여부
- 문자셋/콜레이션 정책
- timezone 정책
- connection pool 정책

### 8. 문서 일관성 계층

현재 확인 파일:

- `README.md`
- 신규 문서: `docs/architecture/mariadb-migration-scope.md`

현재 문제:

- README는 이미 `MariaDB` 사용 프로젝트처럼 보이지만, 실제 코드는 그렇지 않다.

전환 범위:

- 구현 완료 후 README와 실제 설정이 일치하도록 보정
- 운영/개발 실행 가이드에서 DB 준비 절차 반영
- 신규 환경변수 문서 추가

## 이번 전환에서 직접 손대야 하는 1차 대상 파일

구현 단계 기준 1차 수정 후보:

- `shared/database_config.py`
- `park_py/database_config.py`
- `park_py/settings.py`
- `park_py/settings_test.py`
- `park_py/settings_msa_test.py`
- `services/orchestration-service/src/orchestration_service/settings.py`
- `services/parking-command-service/src/parking_command_service/settings.py`
- `services/parking-query-service/src/parking_query_service/settings.py`
- `services/zone-service/src/zone_service/settings.py`
- `services/vehicle-service/src/vehicle_service/settings.py`
- `requirements.txt`
- `Dockerfile`
- `services/orchestration-service/Dockerfile`
- `services/parking-command-service/Dockerfile`
- `services/parking-query-service/Dockerfile`
- `services/zone-service/Dockerfile`
- `services/vehicle-service/Dockerfile`
- 관련 테스트 파일 전반

## 비범위

이번 구현에서 아직 하지 않은 것:

- 실제 MariaDB 인스턴스 프로비저닝
- 운영 DB 데이터 이관 스크립트 작성
- 배포 환경의 DB readiness probe 추가
- Docker image 실제 빌드 검증
- MariaDB 컨테이너 또는 외부 DB 인프라 구성 자동화

## 구현 전 결정해야 할 항목

아래 항목은 현재 구현에서 모두 결정 완료되었다.

### 1. 서비스별 DB 분리 방식

- 현재 alias 구조를 유지해 서비스별로 분리된 MariaDB database를 사용할지
- 하나의 database 안에서 서비스 테이블만 분리할지

결정:

- 현재 구조를 크게 흔들지 않기 위해 서비스별 database 분리 유지

### 2. 표준 Python 드라이버

결정:

- `mysqlclient`
- 로컬 설치 시 `pkg-config`가 없으면 `MYSQLCLIENT_CFLAGS`, `MYSQLCLIENT_LDFLAGS`를 명시해야 할 수 있다.

### 3. 테스트 전략

- 테스트도 MariaDB로 완전히 통일할지
- 테스트만 SQLite를 유지할지

결정:

- 운영 계약과 테스트 계약을 맞추기 위해 MariaDB 기준으로 통일

## 추천 구현 순서

1. DB 연결 계약과 환경변수 규칙 확정
2. Python 드라이버와 Docker OS 패키지 표준 확정
3. 공용 DB 설정 모듈 수정
4. 루트/서비스 settings 수정
5. 테스트 설정과 관련 테스트 수정
6. Dockerfile 및 실행 문서 수정
7. 실제 MariaDB 연결 검증 및 migrate 검증

## 참고 메모

- 현재 루트 `Dockerfile`은 MySQL 계열 개발 라이브러리 설치 흔적이 있다.
- 반대로 각 서비스 Dockerfile은 SQLite 전제를 여전히 강하게 드러낸다.
- 즉, 일부 문서와 일부 빌드 구성은 이미 MariaDB 방향을 암시하지만, 실제 런타임 설정은 아직 SQLite에 고정되어 있다.
- 구현 단계에서는 이 불일치를 먼저 제거하는 것이 핵심이다.
