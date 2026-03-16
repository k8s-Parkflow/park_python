# SQLite3 -> MariaDB 구현 체크리스트

## 진행 상태

- 2026-03-16 기준으로 본 체크리스트의 11개 커밋 단계는 모두 완료되었다.
- 실제 구현은 커밋 병합 없이 단계별로 반영했다.
- 현재 기준 검증 경로는 `mysqlclient`가 설치된 가상환경에서 `manage.py test`를 사용하는 방식이다.

## 목적

- [mariadb-migration-scope.md](/Users/kyum/Desktop/Private/autoE/docs/architecture/mariadb-migration-scope.md)를 실제 구현 가능한 커밋 단위로 분해한다.
- 각 체크리스트 항목은 "하나의 커밋이 하나의 의미"를 가지도록 최소 단위로 나눈다.
- 이 문서는 구현 순서 제안서이며, 아직 실제 코드 변경 내용은 포함하지 않는다.

## 커밋 분해 기준

- 한 커밋은 하나의 책임만 가진다.
- 설정 계약 변경과 의존성 변경은 가능한 한 분리한다.
- 테스트 변경은 그 테스트가 보장하는 계약과 같은 커밋에 포함한다.
- Dockerfile 변경은 런타임/빌드 표준화라는 하나의 의미를 가지도록 묶는다.
- 문서 변경은 구현 결과를 설명하는 최종 정리 커밋으로 분리한다.

## 선행 결정

아래 항목이 정해져야 구현 체크리스트를 그대로 진행할 수 있다.

- MariaDB Python 드라이버 표준 확정
- 서비스별 DB 분리 방식 확정
- 테스트도 MariaDB로 통일할지 여부 확정

권장안:

- 드라이버: `mysqlclient`
- DB 분리 방식: 서비스별 database 분리 유지
- 테스트 전략: MariaDB 기준으로 통일

## 구현 체크리스트

### Commit 1. MariaDB 연결 계약 상수화

목표:

- 공용 DB 설정 모듈에 MariaDB 연결 계약을 표현할 수 있는 상수와 helper 뼈대를 만든다.

변경 대상:

- `shared/database_config.py`
- `park_py/database_config.py`

작업:

- `sqlite3` 파일명 상수 구조를 MariaDB 연결 계약 중심 구조로 교체
- alias별 env key 규칙을 `NAME/HOST/PORT/USER/PASSWORD` 단위로 정의
- MariaDB용 단일 DB 설정 builder 함수 추가
- 다중 서비스 alias 설정 builder 함수가 새 builder를 사용하도록 정리

포함할 테스트:

- `park_py/tests/multi_db/unit/test_ut_msa_database_config.py`

완료 조건:

- 더 이상 공용 DB 설정 모듈이 `django.db.backends.sqlite3`를 반환하지 않는다.
- alias별 설정이 파일 경로가 아닌 연결 정보 dict를 반환한다.
- 단위 테스트가 새 계약을 검증한다.

커밋 의미:

- "프로젝트의 DB 설정 표준을 SQLite 파일 구조에서 MariaDB 연결 구조로 전환"

### Commit 2. 루트 Django settings를 MariaDB 계약으로 전환

목표:

- 통합 앱 `park_py`가 새 공용 DB 계약을 사용하도록 전환한다.

변경 대상:

- `park_py/settings.py`
- 필요 시 `park_py/database_config.py`

포함할 테스트:

- `park_py/tests/multi_db/acceptance/test_at_msa_database_aliases.py`

작업:

- `DATABASES = build_service_databases(...)`가 MariaDB 연결 정보를 생성하도록 반영
- 기존 SQLite 파일명 기대 테스트를 alias/engine/host/name 계약 검증으로 전환

완료 조건:

- 루트 settings가 MariaDB 기반 DB dict를 사용한다.
- 다중 DB alias 구조는 그대로 유지된다.
- acceptance 테스트가 새 계약으로 통과한다.

커밋 의미:

- "루트 통합 Django 앱의 DB 계약 전환"

### Commit 3. 개별 서비스 settings 전환

목표:

- 각 서비스가 개별 실행 시에도 MariaDB 연결 계약을 동일하게 사용하도록 맞춘다.

변경 대상:

- `services/orchestration-service/src/orchestration_service/settings.py`
- `services/parking-command-service/src/parking_command_service/settings.py`
- `services/parking-query-service/src/parking_query_service/settings.py`
- `services/zone-service/src/zone_service/settings.py`
- `services/vehicle-service/src/vehicle_service/settings.py`

포함할 테스트:

- `park_py/tests/runtime/repository/test_rt_orchestration_http_runtime_settings.py`
- `park_py/tests/runtime/repository/test_rt_command_query_http_runtime_settings.py`
- `park_py/tests/runtime/repository/test_rt_internal_service_http_runtime_settings.py`

작업:

- 각 서비스 settings에서 `build_sqlite_database` 의존 제거
- 서비스별 env prefix를 사용하는 MariaDB builder로 교체
- settings 테스트를 `default` alias 존재 여부만이 아니라 DB engine 계약까지 검증하도록 보강

완료 조건:

- 서비스 단독 실행 settings가 모두 같은 MariaDB 계약을 사용한다.
- 런타임 settings 테스트가 새 계약을 검증한다.

커밋 의미:

- "서비스 단독 런타임의 DB 계약 전환"

### Commit 4. 테스트 settings를 MariaDB 테스트 DB 전략으로 교체

목표:

- 테스트 전용 settings가 SQLite 테스트 파일 생성 대신 MariaDB 테스트 DB 전략을 사용하도록 바꾼다.

변경 대상:

- `park_py/settings_test.py`
- `park_py/settings_msa_test.py`

작업:

- `TEST_DB_ROOT`, `.sqlite3` 파일명 조합 제거
- Django `TEST` 설정을 MariaDB용 DB 이름 생성 전략으로 변경
- alias별 테스트 DB 이름 충돌 방지 규칙 적용

완료 조건:

- 테스트 settings에 SQLite 파일 경로 조립 코드가 남아 있지 않다.
- 테스트 DB 이름이 서비스 alias별로 구분된다.

커밋 의미:

- "테스트 런타임 계약을 운영 DB 계열과 일치시킴"

### Commit 5. 테스트 설정 검증 코드 정리

목표:

- 테스트가 더 이상 SQLite 파일명을 가정하지 않도록 전반적인 설정 검증을 정리한다.

변경 대상:

- `park_py/tests/multi_db/unit/test_ut_msa_database_config.py`
- `park_py/tests/multi_db/acceptance/test_at_msa_database_aliases.py`
- `park_py/tests/runtime/repository/test_rt_orchestration_http_runtime_settings.py`
- `park_py/tests/runtime/repository/test_rt_command_query_http_runtime_settings.py`
- `park_py/tests/runtime/repository/test_rt_internal_service_http_runtime_settings.py`

작업:

- 파일명 비교 assertion 제거
- `ENGINE`, `NAME`, `HOST`, `PORT`, `USER` 등 연결 계약 검증으로 변경
- 테스트가 서비스별 env override를 검증하도록 수정

완료 조건:

- 테스트 코드에 `*.sqlite3` 문자열 기대가 남아 있지 않다.
- 설정/런타임 검증 테스트가 MariaDB 계약을 직접 보장한다.

커밋 의미:

- "테스트 검증 기준을 SQLite 파일명에서 MariaDB 연결 계약으로 전환"

### Commit 6. Python DB 드라이버 의존성 반영

목표:

- Django가 MariaDB에 실제 연결할 수 있도록 Python 패키지 의존성을 반영한다.

변경 대상:

- `requirements.txt`

작업:

- 선택한 MariaDB 드라이버 추가
- 필요 시 주석 또는 문서상 드라이버 표준 근거 정리

완료 조건:

- requirements에 운영 표준 드라이버가 포함된다.

커밋 의미:

- "MariaDB 연결을 위한 Python 런타임 의존성 추가"

### Commit 7. 루트 Dockerfile의 MariaDB 빌드 표준화

목표:

- 루트 Dockerfile이 선택한 MariaDB 드라이버에 맞는 OS 패키지 조합을 사용하도록 정리한다.

변경 대상:

- `Dockerfile`

작업:

- 드라이버 빌드/런타임에 필요한 OS 패키지만 남기도록 조정
- 주석을 현재 표준과 일치시키도록 정리

완료 조건:

- 루트 Dockerfile이 requirements의 MariaDB 드라이버와 모순되지 않는다.

커밋 의미:

- "루트 컨테이너 빌드 환경을 MariaDB 표준에 맞춤"

### Commit 8. 서비스 Dockerfile의 SQLite 전제 제거

목표:

- 각 서비스 Dockerfile에서 SQLite 파일 중심 설명과 권한 전제를 제거한다.

변경 대상:

- `services/orchestration-service/Dockerfile`
- `services/parking-command-service/Dockerfile`
- `services/parking-query-service/Dockerfile`
- `services/zone-service/Dockerfile`
- `services/vehicle-service/Dockerfile`

작업:

- SQLite 전용 주석 제거
- 드라이버에 맞는 OS 패키지 설치로 통일
- DB 파일 쓰기 전제의 과도한 권한 부여가 불필요하면 제거 또는 축소

완료 조건:

- 서비스 Dockerfile 어디에도 SQLite 전용 전제가 남아 있지 않다.
- 빌드 의존성이 루트 표준과 일치한다.

커밋 의미:

- "서비스 컨테이너를 MariaDB 런타임 전제로 정리"

### Commit 9. 실행/마이그레이션 스크립트의 DB 환경변수 계약 반영

목표:

- 서비스 실행 및 마이그레이션 스크립트가 MariaDB 환경변수 계약을 사용하도록 정리한다.

변경 대상:

- `scripts/services/orchestration/migrate.sh`
- `scripts/services/parking-command/migrate.sh`
- `scripts/services/parking-query/migrate.sh`
- `scripts/services/zone/migrate.sh`
- `scripts/services/vehicle/migrate.sh`
- 필요 시 `scripts/services/*/run_*.sh`

작업:

- 스크립트에서 필요한 환경변수 목록 명시
- 필요 시 DB readiness 체크 추가 여부 결정
- migrate 실행 전제와 사용 예시 정리

완료 조건:

- 서비스별 실행 스크립트가 MariaDB 연결 환경을 전제로 동작한다.
- 운영자가 어떤 env를 넣어야 하는지 코드/스크립트 수준에서 드러난다.

커밋 의미:

- "실행 스크립트 레벨에서 MariaDB 운영 계약 반영"

### Commit 10. MariaDB 연결 회귀 테스트 추가

목표:

- 단순 설정 교체를 넘어서, 실제 MariaDB 기준 연결 계약이 유지되는지 회귀 테스트를 추가한다.

변경 대상:

- 기존 설정 테스트 파일
- 필요 시 신규 runtime/repository 테스트

작업:

- env override가 서비스별로 정확히 반영되는지 검증
- `ENGINE`, `TEST.NAME`, alias 구조, 단일 서비스 settings 계약 검증 보강

완료 조건:

- 설정 회귀가 생기면 테스트가 즉시 실패한다.
- SQLite로 되돌아가는 실수를 테스트가 잡을 수 있다.

커밋 의미:

- "MariaDB 설정 회귀 방지 테스트 보강"

### Commit 11. 운영 문서와 README 정합성 정리

목표:

- 구현 완료 후 문서와 실제 코드 상태를 일치시킨다.

변경 대상:

- `README.md`
- `docs/architecture/mariadb-migration-scope.md`
- 필요 시 신규 운영 문서

작업:

- 실제 사용 DB를 MariaDB로 명시
- 필요한 환경변수와 로컬/운영 실행 예시 정리
- SQLite 전제 설명 제거

완료 조건:

- README와 실제 설정이 충돌하지 않는다.
- 신규 참여자가 DB 실행 방법을 문서만 보고 파악할 수 있다.

커밋 의미:

- "구현 결과를 문서에 반영해 운영 가이드 정리"

## 권장 실행 순서

1. Commit 1
2. Commit 2
3. Commit 3
4. Commit 4
5. Commit 5
6. Commit 6
7. Commit 7
8. Commit 8
9. Commit 9
10. Commit 10
11. Commit 11

## 커밋 병합 가능 구간

리뷰 효율보다 속도가 더 중요할 때만 아래 묶음을 고려할 수 있다.

- Commit 1 + Commit 2
  - 공용 DB 설정과 루트 settings를 한 번에 반영
- Commit 4 + Commit 5
  - 테스트 settings 변경과 테스트 assertion 변경을 한 번에 반영
- Commit 7 + Commit 8
  - Docker 표준화 작업을 한 번에 반영

기본 권장:

- 위 병합 없이 분리 유지

## 구현 시 주의사항

- 기존 user 변경분이 있는 파일은 덮어쓰지 말고 병행 반영한다.
- `transaction`, repository, domain 로직은 이번 전환의 직접 대상이 아니다.
- 테스트를 SQLite만 통과하도록 우회하면 운영과 테스트 계약이 다시 어긋난다.
- Docker 권한 축소는 DB 전환과 함께 하되, 서비스 실행 스크립트와 충돌하지 않는지 별도 검증이 필요하다.
