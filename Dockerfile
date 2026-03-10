# 1. 빌드 스테이지 (의존성 설치 및 가상환경 생성)
FROM python:3.11-slim AS builder

WORKDIR /app

# 빌드 시 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 가상환경 생성 및 패키지 설치
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn  # gunicorn 명시적 설치

# 2. 실행 스테이지 (실제 런타임 이미지)
FROM python:3.11-slim

WORKDIR /app

# 보안: Non-root 사용자 생성 (appuser)
RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --create-home --home-dir /app appuser

# 실행 시 필요한 최소 라이브러리 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 빌더 스테이지에서 가상환경 복사
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 프로젝트 소스 복사 및 소유권 변경
COPY --chown=appuser:appgroup . .

# 일반 사용자 권한으로 전환
USER appuser

EXPOSE 8000

# Gunicorn을 통한 실행 (park_py.wsgi 사용)
# --workers 3: 보통 (CPU 코어 수 * 2) + 1 권장
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "park_py.wsgi:application", "--workers", "3", "--timeout", "120"]
