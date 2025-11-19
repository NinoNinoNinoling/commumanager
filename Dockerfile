# ============================================================================
# 마녀봇 Dockerfile (멀티 스테이지 빌드)
# ============================================================================
# Stage 1: Base
FROM python:3.11-slim as base

# 작업 디렉토리
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Flask Web App
FROM base as web

WORKDIR /app

# 애플리케이션 코드 복사
COPY admin_web/ ./admin_web/
COPY init_db.py .
COPY .env.example .

# 포트 노출
EXPOSE 5000

# Flask 앱 실행
CMD ["python", "-m", "flask", "--app", "admin_web/app.py", "run", "--host=0.0.0.0"]

# ============================================================================
# Stage 3: Bot
FROM base as bot

WORKDIR /app

# 봇 코드 복사
COPY bot/ ./bot/
COPY init_db.py .
COPY .env.example .

# 봇 실행
CMD ["python", "-m", "bot.reward_bot"]

# ============================================================================
# Stage 4: Celery Worker
FROM base as celery-worker

WORKDIR /app

# 봇 코드 복사 (Celery tasks 포함)
COPY bot/ ./bot/
COPY init_db.py .
COPY .env.example .

# Celery Worker 실행
CMD ["celery", "-A", "bot.tasks", "worker", "--loglevel=info"]

# ============================================================================
# Stage 5: Celery Beat
FROM base as celery-beat

WORKDIR /app

# 봇 코드 복사
COPY bot/ ./bot/
COPY init_db.py .
COPY .env.example .

# Celery Beat 실행 (스케줄러)
CMD ["celery", "-A", "bot.tasks", "beat", "--loglevel=info"]
