# 1단계: 빌드 스테이지 (의존성 설치 전용)
FROM python:3.11-slim AS builder
WORKDIR /app

# SQLite3는 별도의 dev 라이브러리가 필요 없으므로 gcc 정도만 설치 (일부 라이브러리 빌드용)
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

# SQLite DB 파일이 저장될 디렉토리 권한 설정 (필요 시)
# 만약 컨테이너 내부에서 DB 파일을 생성한다면 해당 폴더에 쓰기 권한이 있어야 합니다.
RUN chmod -R 777 /app

# 스크립트 권한 부여
RUN chmod +x scripts/services/orchestration/*.sh

EXPOSE 8000

# 실행 명령
CMD ["./scripts/services/orchestration/run_http.sh"]
