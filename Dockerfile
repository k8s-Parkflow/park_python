# 1. 빌드 스테이지
FROM python:3.11-slim AS builder
WORKDIR /app

# mysqlclient 빌드를 위해 MariaDB/MySQL 클라이언트 헤더와 pkg-config가 필요하다.
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

# 빌드된 mysqlclient wheel이 링크할 런타임 공유 라이브러리만 유지한다.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 && rm -rf /var/lib/apt/lists/*

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
