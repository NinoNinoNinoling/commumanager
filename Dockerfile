FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 데이터베이스 초기화 (빌드 시)
RUN python init_db.py

# 포트 노출
EXPOSE 5000

# Gunicorn으로 실행
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "admin_web.app:create_app()"]
