# 1단계: 빌드 스테이지
FROM python:3.11-slim AS builder
WORKDIR /app

# mysqlclient 빌드를 위해 MariaDB/MySQL 클라이언트 헤더와 pkg-config가 필요하다.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Python 의존성 설치
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------

# 2단계: 실행 스테이지
FROM python:3.11-slim
WORKDIR /app

# 빌드된 mysqlclient wheel이 링크할 런타임 공유 라이브러리만 유지한다.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

# 빌드 스테이지에서 생성된 가상환경 복사
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

# parking-query 서비스 스크립트 실행 권한 부여
RUN chmod +x scripts/services/parking-query/*.sh

# parking-query gRPC 기본 포트
EXPOSE 50018

# gRPC 실행 스크립트 호출
CMD ["./scripts/services/parking-query/run_grpc.sh"]
