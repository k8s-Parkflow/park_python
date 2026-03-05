# 엔터티 커버리지(coverage.py) 기본 실행 가이드

## 1) 사전 준비

```bash
./.venv/bin/python -m pip install coverage
```

## 2) 엔터티 커버리지 측정

```bash
./scripts/run_entity_coverage.sh
```

## 3) 리포트 파일 생성

- 실행 스크립트는 정규화된 고정 파일명으로만 산출물을 생성한다.
- 리포트 텍스트: `reports/coverage/entities/entity_coverage_report.txt`
- XML: `reports/coverage/entities/entity_coverage.xml`
- JSON: `reports/coverage/entities/entity_coverage.json`
- Raw data: `reports/coverage/entities/entity_coverage.data`

## 4) 참고

- 현재 `reports/coverage/.coveragerc`는 아래 엔터티 `models` 디렉토리만 측정한다.
  - `services/parking-command-service/src/parking_command_service/models`
  - `services/parking-query-service/src/parking_query_service/models`
  - `services/vehicle-service/src/vehicle_service/models`
  - `services/zone-service/src/zone_service/models`
- 마이그레이션과 `__init__.py`는 측정에서 제외한다.
