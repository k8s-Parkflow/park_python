# 공통 이미지와 Dockerfile

## 1. 이미지 전략

현재 저장소는 서비스별 소스가 하나의 리포지토리 안에 있고, 런타임도 같은 Django 프로젝트를 공유한다. 따라서 이미지는 서비스마다 따로 만들기보다 공통 이미지 1개를 만들고, Kubernetes 에서 `command` 만 바꿔 재사용하는 방식이 가장 단순하다.

예시:

- 같은 이미지 사용
- `gateway-http` 는 `gunicorn`
- `vehicle-grpc` 는 `python manage.py run_vehicle_grpc`
- `zone-grpc` 는 `python manage.py run_zone_grpc`
- `parking-command-grpc` 는 `python manage.py run_parking_command_grpc`
- `parking-query-grpc` 는 `python manage.py run_parking_query_grpc`

## 2. 운영용 의존성

현재 `requirements.txt` 에는 최소 Django 의존성만 있다. 운영 배포 전에는 최소한 아래 패키지를 포함해야 한다.

- `grpcio`
- `protobuf`
- `gunicorn`
- MySQL 사용 시 `mysqlclient`

현재 저장소 기준 실제 빌드 검증 결과:

- 루트 `Dockerfile` 빌드 통과
- `services/orchestration-service/Dockerfile` 빌드 통과
- `services/parking-command-service/Dockerfile` 빌드 통과
- `services/parking-query-service/Dockerfile` 빌드 통과
- `services/vehicle-service/Dockerfile` 빌드 통과
- `services/zone-service/Dockerfile` 빌드 통과

예시:

```txt
Django==4.2.29
djangorestframework==3.16.1
drf-spectacular==0.29.0
grpcio==1.74.0
protobuf==5.29.5
gunicorn==22.0.0
mysqlclient==2.2.4
```

버전은 팀 기준에 맞춰 조정하면 되지만, 이미지 안에는 HTTP/gRPC 실행에 필요한 패키지가 모두 있어야 한다.

## 3. 권장 Dockerfile

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

RUN groupadd --system appgroup && useradd --system --gid appgroup appuser
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=park_py.settings_prod

COPY --chown=appuser:appgroup . .

USER appuser
```

## 4. 서비스별 컨테이너 실행 명령

### HTTP gateway

```yaml
command: ["gunicorn"]
args: ["park_py.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
ports:
  - containerPort: 8000
```

### vehicle gRPC

```yaml
command: ["python", "manage.py", "run_vehicle_grpc"]
ports:
  - containerPort: 50051
```

### zone gRPC

```yaml
command: ["python", "manage.py", "run_zone_grpc"]
ports:
  - containerPort: 50052
```

### parking-command gRPC

```yaml
command: ["python", "manage.py", "run_parking_command_grpc"]
ports:
  - containerPort: 50053
```

### parking-query gRPC

```yaml
command: ["python", "manage.py", "run_parking_query_grpc"]
ports:
  - containerPort: 50054
```

## 5. 공통 환경 변수

모든 파드에 공통으로 들어갈 가능성이 높은 항목이다.

```yaml
env:
  - name: DJANGO_SETTINGS_MODULE
    value: park_py.settings_prod
  - name: SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: autoe-app-secret
        key: SECRET_KEY
  - name: ALLOWED_HOSTS
    value: "autoe.example.com,gateway-http"
```

## 6. 운영 체크 포인트

- 프로덕션에서는 `runserver` 를 쓰지 않는다.
- 동일 이미지를 재사용하면 빌드와 롤백이 단순해진다.
- 서비스별 차이는 이미지가 아니라 `command`, `port`, `env` 로 표현한다.
