# 1. 빌드 스테이지
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# 가상환경을 만들고 필요한 패키지만 설치
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 2. 실행 스테이지
FROM python:3.11-slim
WORKDIR /app

# 실행에 필요한 최소 라이브러리 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# 빌드된 가상환경 복사
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 소스 복사 (현재 폴더의 모든 내용을 /app으로)
COPY . .

# Orchestration 서비스 소스 경로 추가
ENV PYTHONPATH="/app:/app/services/orchestration-service/src"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
