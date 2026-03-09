# parking-query-service Zone Availability API

## 목적

- 전체 Zone 기준 타입별 여석 총합 조회 API를 명확히 정의한다.
- 요청 조건, 응답 형식, 오류 계약, 실행 및 검증 방법을 한 번에 확인할 수 있도록 정리한다.

## 엔드포인트

- `GET /api/zones/availabilities`

## Swagger 경로

- Swagger UI: `GET /api/docs/`
- OpenAPI Schema: `GET /api/schema/`

## 기능 요약

- `slot_type`를 전달하면 해당 타입의 전체 Zone 여석 총합을 반환한다.
- `slot_type`를 생략하면 지원하는 전체 타입의 전체 Zone 여석 총합을 반환한다.
- 지원 타입은 `GENERAL`, `EV`, `DISABLED`다.
- 지원 타입 값은 대소문자를 구분하지 않는다.
- 타입별 조회 응답은 `slotType`, `availableCount` 두 필드를 반환한다.
- 전체 조회 응답은 `availableCount` 한 필드만 반환한다.

## Query Parameters

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `slot_type` | `string` | N | 조회할 슬롯 타입. `GENERAL`, `EV`, `DISABLED` 지원 |

## 정상 응답

### 1. 일반 타입 전체 여석 조회

요청:

```http
GET /api/zones/availabilities?slot_type=GENERAL
```

응답:

```json
{
  "slotType": "GENERAL",
  "availableCount": 12
}
```

### 2. 전기차 타입 전체 여석 조회

요청:

```http
GET /api/zones/availabilities?slot_type=EV
```

응답:

```json
{
  "slotType": "EV",
  "availableCount": 5
}
```

### 3. 장애인 타입 전체 여석 조회

요청:

```http
GET /api/zones/availabilities?slot_type=DISABLED
```

응답:

```json
{
  "slotType": "DISABLED",
  "availableCount": 6
}
```

### 4. 전체 타입 전체 여석 조회

요청:

```http
GET /api/zones/availabilities
```

응답:

```json
{
  "availableCount": 23
}
```

### 5. 집계 데이터가 없는 타입 조회

요청:

```http
GET /api/zones/availabilities?slot_type=EV
```

응답:

```json
{
  "slotType": "EV",
  "availableCount": 0
}
```

설명:
- 지원하는 타입이지만 집계 데이터가 없으면 오류가 아니라 `0`을 반환한다.

### 6. 혼합 대소문자 타입 조회

요청:

```http
GET /api/zones/availabilities?slot_type=GeNeRaL
```

응답:

```json
{
  "slotType": "GENERAL",
  "availableCount": 12
}
```

설명:
- 입력값은 표준 대문자 타입으로 정규화된다.

## 오류 응답

### 지원하지 않는 타입 요청

요청:

```http
GET /api/zones/availabilities?slot_type=VIP
```

응답:

```json
{
  "error": {
    "code": "bad_request",
    "message": "잘못된 요청입니다.",
    "details": {
      "slot_type": [
        "지원하지 않는 슬롯 타입입니다."
      ]
    }
  }
}
```

상태 코드:
- `400 Bad Request`

## 계산 기준

- 집계 기준 엔터티는 `ZONE_AVAILABILITY`다.
- 타입별 합계는 전체 Zone에 속한 동일 `slot_type`의 `available_count` 합이다.
- 전체 합계는 지원하는 전체 타입 `GENERAL`, `EV`, `DISABLED`의 `available_count` 합이다.
- `available_count`는 `total_count - occupied_count`를 만족해야 하며 음수가 될 수 없다.
- 응답에 Zone별 상세 목록은 포함하지 않는다.

## 실행 방법

### 1. 의존성 설치

```bash
./.venv/bin/pip install -r requirements.txt
```

### 2. 마이그레이션 적용

```bash
./.venv/bin/python manage.py migrate
```

### 3. 서버 실행

```bash
./.venv/bin/python manage.py runserver
```

실행 후 접근 경로:
- API: `http://localhost:8000/api/zones/availabilities`
- Swagger UI: `http://localhost:8000/api/docs/`
- Schema JSON: `http://localhost:8000/api/schema/?format=json`


샘플 데이터 기준 예상 결과:
- `GENERAL` 합계: `12`
- `EV` 합계: `5`
- `DISABLED` 합계: `6`
- 전체 합계: `23`

## API 검증 방법

### 1. Swagger UI로 수동 검증

접속:

```text
http://localhost:8000/api/docs/
```

권장 확인 케이스:
- `slot_type=GENERAL`
- `slot_type=EV`
- `slot_type=DISABLED`
- `slot_type` 미입력
- `slot_type=VIP`
- `slot_type=GeNeRaL`

### 2. curl로 수동 검증

```bash
curl -X GET "http://localhost:8000/api/zones/availabilities?slot_type=GENERAL" -H "accept: application/json"
curl -X GET "http://localhost:8000/api/zones/availabilities?slot_type=DISABLED" -H "accept: application/json"
curl -X GET "http://localhost:8000/api/zones/availabilities" -H "accept: application/json"
curl -X GET "http://localhost:8000/api/zones/availabilities?slot_type=VIP" -H "accept: application/json"
curl -X GET "http://localhost:8000/api/zones/availabilities?slot_type=GeNeRaL" -H "accept: application/json"
```

### 3. OpenAPI Schema 검증

```bash
curl -X GET "http://localhost:8000/api/schema/?format=json" -H "accept: application/json"
```

확인 포인트:
- `/api/zones/availabilities` 경로 존재
- query parameter `slot_type` 존재
- `200` 응답 존재
- `400` 응답 존재

### 4. 자동 테스트 검증

```bash
./.venv/bin/python manage.py test acceptance contract unit repository --settings=park_py.settings_test
```

현재 기준 기대 결과:
- `27 tests OK`
