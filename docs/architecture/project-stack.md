# 프로젝트 버전 및 의존성 기준

## 목적

- 현재 저장소에서 확인 가능한 프레임워크/런타임 기준을 문서화한다.
- 신규 코드 작성 시 버전 미스매치를 줄이기 위한 최소 기준을 남긴다.
- 의존성 파일이 없는 상태에서 추정이 아니라 저장소 근거 기반으로 판단한다.

## 현재 프로젝트 기준

- Django: `4.2.29`
- 데이터베이스: `SQLite3`
- 로컬 실행 Python: `3.9.18 (PyPy 7.3.13)`

## 사용중인 의존성

- Django 4.2.29
- 표준 라이브러리
- in-repo Django apps
  - `parking_command_service`
  - `parking_query_service`
  - `zone_service`
  - `vehicle_service`

## 주의사항

- 현재 저장소에는 `requirements.txt`, `pyproject.toml`, `Pipfile` 같은 의존성 명세 파일이 없다.
- 저장소 일부 코드에는 `datetime | None` 같은 Python 3.10+ 문법이 이미 섞여 있다.
- 반면 현재 Codex 작업 환경에서 확인된 Python 런타임은 3.9.18이다.
- 따라서 신규 공통 인프라 코드는 런타임 호환성이 명확해질 때까지 Python 3.9에서도 안전한 타입 힌트 문법(`Optional`, `Union`)을 우선한다.

## 신규 코드 작성 기준

- Django API/예외 처리 코드는 Django 4.2 기준으로 작성한다.
- 외부 라이브러리는 의존성 명세 파일이 추가되기 전까지 임의로 도입하지 않는다.
- 공통 모듈에서는 Python 버전 의존성이 큰 최신 문법 도입을 보수적으로 판단한다.
- 실제 프로젝트 표준 버전은 추후 `pyproject.toml` 또는 `requirements.txt` 로 확정한다.
