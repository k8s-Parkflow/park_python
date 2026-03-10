# parking-query-service 커버리지(coverage.py) 산출물

## 1) 목적

- 현재 브랜치에서 변경한 `parking-query-service` API 코드의 커버리지 산출물 위치와 측정 방법을 정리한다.
- 특히 전체 Zone 기준 타입별/전체 여석 조회 기능의 보장 범위를 빠르게 확인할 수 있도록 한다.

## 2) 실행 명령

```bash
./scripts/run_project_coverage.sh acceptance contract unit repository
```

## 3) 산출물 파일

- 텍스트 리포트: `reports/coverage/project/project_coverage_report.txt`
- XML: `reports/coverage/project/project_coverage.xml`
- JSON: `reports/coverage/project/project_coverage.json`
- Raw data: `reports/coverage/project/project_coverage.data`

## 4) 측정 기준

- 측정 스크립트는 `reports/coverage/.coveragerc.project`를 사용한다.
- `services`와 `park_py` 전체를 측정 대상으로 삼는다.
- 마이그레이션, `__init__.py`, 테스트 코드는 측정에서 제외한다.

## 5) 이번 브랜치 핵심 코드 커버리지

기준 실행:

```bash
./scripts/run_project_coverage.sh acceptance contract unit repository
```

핵심 production 코드 결과:

| 파일 | 커버리지 | 비고 |
| --- | --- | --- |
| `services/parking-query-service/src/parking_query_service/repositories/zone_availability_repository.py` | `100.00%` | 타입별/전체 조회용 집계 repository |
| `services/parking-query-service/src/parking_query_service/serializers.py` | `100.00%` | Swagger/OpenAPI schema serializer |
| `services/parking-query-service/src/parking_query_service/services/zone_availability_service.py` | `100.00%` | 타입 검증, 정규화, 합산 로직 |
| `services/parking-query-service/src/parking_query_service/views.py` | `100.00%` | DRF endpoint 및 OpenAPI 설명 |
| `park_py/settings.py` | `90.24%` | Swagger 설정 포함 공통 Django 설정 |
| `park_py/urls.py` | `88.24%` | API/Swagger URL 등록 |

## 6) 해석

- 기능 핵심 코드인 `repository`, `serializers`, `service`, `view`는 모두 `100%` 커버.
- 남은 미커버는 공통 설정 파일에 집중되어 있다.
- `park_py/urls.py`의 미커버 라인은 admin URL append 분기다.
- `park_py/settings.py`의 미커버는 `sys.path` 삽입 분기의 branch coverage다.

## 7) 전체 프로젝트 결과 참고

- 전체 프로젝트 총 커버리지는 `76.14%` (현재 브랜치 변경 범위 밖의 기존 코드 미커버까지 포함한 값)
- 브랜치에서 실제로 추가/수정한 `parking-query-service` API 핵심 코드는 `100%` 커버

## 8) 검증 명령

기능 회귀 검증:

```bash
./.venv/bin/python manage.py test acceptance contract unit repository --settings=park_py.settings_test
```

현재 기준 기대 결과:

- `27 tests OK`
