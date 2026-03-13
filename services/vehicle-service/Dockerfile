# 1단계: 빌드 스테이지
FROM python:3.11-slim AS builder
WORKDIR /app

# SQLite3는 별도 라이브러리가 필요 없으므로 gcc만 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# pip 및 패키지 설치 (mysqlclient 제외)
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------

# 2단계: 실행 스테이지
FROM python:3.11-slim
WORKDIR /app

# 빌드 스테이지에서 설치된 venv 복사
COPY --from=builder /opt/venv /opt/venv

# 환경 변수 설정
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 소스 코드 복사
COPY . .

# SQLite DB 쓰기 권한 및 스크립트 실행 권한 부여
RUN chmod -R 777 /app && \
    chmod +x scripts/services/vehicle/*.sh

# vehicle gRPC 기본 포트
EXPOSE 50015

# gRPC 실행 스크립트 호출
CMD ["./scripts/services/vehicle/run_grpc.sh"]
