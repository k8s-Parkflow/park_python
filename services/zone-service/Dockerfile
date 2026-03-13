# 1단계: 빌드 스테이지
FROM python:3.11-slim AS builder
WORKDIR /app

# SQLite3 환경을 위한 최소 빌드 도구만 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# mysqlclient 제외하고 의존성 설치
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------

# 2단계: 실행 스테이지
FROM python:3.11-slim
WORKDIR /app

# 빌드 스테이지에서 생성된 가상환경 복사
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

# SQLite DB 쓰기 및 zone 서비스 스크립트 실행 권한 부여
RUN chmod -R 777 /app && \
    chmod +x scripts/services/zone/*.sh

# zone gRPC 기본 포트
EXPOSE 50052

# gRPC 실행 스크립트 호출
CMD ["./scripts/services/zone/run_grpc.sh"]
