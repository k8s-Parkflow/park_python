# 1단계: 빌드 스테이지
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

# -----------------------------------------------------------

# 2단계: 실행 스테이지
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

COPY manage.py .
COPY park_py/ ./park_py/
COPY shared/ ./shared/
COPY contracts/ ./contracts/
COPY services/ ./services/
COPY scripts/ ./scripts/

ENV PYTHONPATH="/app:/app/services/parking-query-service/src:/app/contracts/gen/python"
ENV DJANGO_SETTINGS_MODULE=parking_query_service.settings

RUN chmod +x scripts/services/parking-query/*.sh && \
    chmod +x scripts/services/_common.sh

EXPOSE 50051

CMD ["./scripts/services/parking-query/run_grpc.sh"]
