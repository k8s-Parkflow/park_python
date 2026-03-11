# 1단계: 빌드 스테이지
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# 패키지를 /install 폴더에 모아서 설치
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# 2단계: 실행 스테이지
FROM python:3.11-slim

WORKDIR /app

# 실행 시 필요한 런타임 라이브러리만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 빌드된 패키지들을 시스템 경로(/usr/local)로 복사
COPY --from=builder /install /usr/local
COPY . .

ENV PYTHONPATH="/app:/app/services/parking-zone-service/src"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
