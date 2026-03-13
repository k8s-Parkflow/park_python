# API 문서 가이드

이 폴더는 현재 프로젝트의 HTTP API를 기능별로 정리한 문서 모음입니다.

기본 실행 기준:
- 루트 Django 앱(`park_py`) 실행 시 하나의 서버에서 모든 공개/내부 HTTP API를 확인할 수 있습니다.
- 기본 문서 경로:
  - Swagger UI: `/api/docs/swagger`
  - OpenAPI JSON: `/api/docs/openapi.json`

문서 목록:
- `public-query-api.md`
- `gateway-api.md`
- `integration-guide.md`
- `internal-support-api.md`
- `internal-command-api.md`
- `internal-query-api.md`

## 공통 응답 규칙

정상 응답은 기능별 payload를 그대로 JSON으로 반환합니다.

에러 응답은 공통적으로 아래 형태를 따릅니다.

```json
{
  "error": {
    "code": "bad_request",
    "message": "잘못된 요청입니다.",
    "details": {
      "field_name": ["에러 메시지"]
    }
  }
}
```

대표 `code`:
- `bad_request`
- `not_found`
- `conflict`
- `internal_server_error`

관련 코드:
- 공통 에러 응답 빌더: `shared/error_handling/responses.py`
- 메인 URL 진입점: `park_py/urls.py`
- Swagger UI + CSRF 설정: `park_py/openapi.py`

## 호출 시 참고

- `GET` API는 일반 브라우저/Swagger/curl로 확인하기 쉽습니다.
- 일부 공개 `POST` API는 Django CSRF 보호를 받습니다.
  - 브라우저에서 테스트할 때는 `/api/docs/swagger` 사용을 권장합니다.
  - Swagger UI가 CSRF 쿠키와 `X-CSRFToken` 헤더를 자동으로 붙이도록 구현되어 있습니다.
- 내부 `POST` API 일부는 서비스 간 호출을 위해 `csrf_exempt` 처리되어 있습니다.

## 빠른 분류

공개 API:
- 전체 여석 조회
- 존별 슬롯 목록 조회
- 차량 현재 위치 조회
- 사가 기반 입차/출차
- 사가 상태 조회

내부 API:
- 차량 조회
- 슬롯 입차 정책 조회
- parking-command write/compensation
- parking-query projection/read model 반영

## 문서 해석 기준

- 프론트엔드는 `gateway-api.md`와 `public-query-api.md`를 기준으로 연동합니다.
- 입차/출차는 `gateway-api.md` 기준으로 진행합니다.
- 내부 `parking-command`, `parking-query`, `vehicle`, `zone` API는 서비스 간 연동용입니다.
