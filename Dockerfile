# 1. 빌드 스테이지
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 2. 실행 스테이지
FROM python:3.11-slim
WORKDIR /app

# Non-root 사용자 생성 (보안)
RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# 빌드된 가상환경 복사
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 소스 코드 전체 복사 및 권한 부여
COPY --chown=appuser:appgroup . .

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

USER appuser
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
