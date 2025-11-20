# 마녀봇 배포 가이드

마스토돈 커뮤니티 관리 봇의 전체 배포 및 설정 가이드입니다.

---

## 📋 목차

1. [사전 요구사항](#1-사전-요구사항)
2. [서버 준비](#2-서버-준비)
3. [DuckDNS 도메인 설정](#3-duckdns-도메인-설정)
4. [마스토돈 서버 설치](#4-마스토돈-서버-설치)
5. [마녀봇 설치](#5-마녀봇-설치)
6. [Docker로 실행](#6-docker로-실행)
7. [관리자 웹 설정](#7-관리자-웹-설정)
8. [문제 해결](#8-문제-해결)

---

## 1. 사전 요구사항

### 필수 소프트웨어
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+
- Git

### 권장 서버 스펙
- CPU: 2 vCPU 이상
- RAM: 4GB 이상
- 디스크: 30GB 이상
- OS: Ubuntu 22.04 LTS

### 설치 확인
```bash
docker --version
docker-compose --version
python3 --version
git --version
```

---

## 2. 서버 준비

### 2.1 클라우드 인스턴스 생성

**추천 클라우드 플랫폼:**

#### Oracle Cloud (무료)
- 리전: 춘천 (ap-chuncheon-1)
- 머신: Ampere A1 (4 OCPU, 24GB RAM)
- OS: Ubuntu 22.04 LTS
- 스토리지: 200GB

#### Google Cloud Platform
- 리전: asia-northeast3 (서울)
- 머신: E2 e2-medium (2 vCPU, 4GB) 이상
- OS: Ubuntu 22.04 LTS
- 디스크: 30GB 이상

### 2.2 기본 패키지 설치

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y \
  docker.io \
  docker-compose \
  git \
  nginx \
  certbot \
  python3-certbot-nginx \
  python3-pip \
  build-essential \
  curl \
  wget

# Docker 권한 설정
sudo usermod -aG docker $USER
newgrp docker

# 시간대 설정
sudo timedatectl set-timezone Asia/Seoul
```

---

## 3. DuckDNS 도메인 설정

### 3.1 도메인 등록
1. https://www.duckdns.org 로그인
2. 서브도메인 생성 (예: yourserver.duckdns.org)
3. 서버 IP 입력

### 3.2 IP 자동 업데이트
```bash
mkdir -p ~/duckdns && cd ~/duckdns

cat > duck.sh << 'EOF'
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=YOUR_DOMAIN&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF

chmod +x duck.sh
./duck.sh
cat duck.log  # "OK" 확인

# Cron 등록 (5분마다 업데이트)
crontab -e
# 추가: */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

---

## 4. 마스토돈 서버 설치

### 4.1 저장소 클론
```bash
cd ~
git clone https://github.com/whippyshou/mastodon.git
cd mastodon
```

### 4.2 시크릿 키 생성
```bash
cp .env.production.sample .env.production

# 시크릿 키 3개 생성
docker-compose run --rm web bundle exec rake secret  # SECRET_KEY_BASE
docker-compose run --rm web bundle exec rake secret  # OTP_SECRET
docker-compose run --rm web bundle exec rake mastodon:webpush:generate_vapid_key
```

### 4.3 환경 변수 설정
```bash
nano .env.production
```

**필수 설정:**
```bash
# 도메인
LOCAL_DOMAIN=yourserver.duckdns.org
WEB_DOMAIN=yourserver.duckdns.org

# 데이터베이스
REDIS_HOST=redis
REDIS_PORT=6379
DB_HOST=db
DB_USER=postgres
DB_NAME=postgres
DB_PASS=CHANGE_THIS_PASSWORD
DB_PORT=5432

# 시크릿 키 (위에서 생성한 값 입력)
SECRET_KEY_BASE=your_generated_secret_1
OTP_SECRET=your_generated_secret_2
VAPID_PRIVATE_KEY=your_generated_vapid_private
VAPID_PUBLIC_KEY=your_generated_vapid_public

# SMTP (SendGrid 무료 플랜 권장)
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_LOGIN=apikey
SMTP_PASSWORD=YOUR_SENDGRID_API_KEY
SMTP_FROM_ADDRESS=noreply@yourserver.duckdns.org
```

### 4.4 마스토돈 실행
```bash
# 빌드 및 실행
docker-compose up -d

# DB 마이그레이션
docker-compose run --rm web rails db:migrate

# 자산 사전 컴파일
docker-compose run --rm web rails assets:precompile

# 관리자 계정 생성
docker-compose run --rm web bin/tootctl accounts create \
  admin \
  --email admin@yourserver.duckdns.org \
  --confirmed \
  --role Owner
```

---

## 5. 마녀봇 설치

### 5.1 저장소 클론
```bash
cd ~
git clone https://github.com/NinoNinoNinoling/commumanager.git
cd commumanager
```

### 5.2 환경 변수 설정
```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 편집
nano .env
```

**필수 설정 항목:**
```bash
# 마스토돈 인스턴스
MASTODON_INSTANCE_URL=https://yourserver.duckdns.org
MASTODON_CLIENT_ID=your_client_id
MASTODON_CLIENT_SECRET=your_client_secret

# 봇 액세스 토큰
BOT_ACCESS_TOKEN=your_bot_access_token

# PostgreSQL (마스토돈 서버 DB)
POSTGRES_HOST=yourserver.duckdns.org  # 또는 서버 IP
POSTGRES_PORT=5432
POSTGRES_DB=mastodon_production
POSTGRES_USER=mastodon
POSTGRES_PASSWORD=your_postgres_password

# Flask 시크릿 키 (랜덤 생성)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 관리자 계정 ID (마스토돈에서 확인)
ADMIN_ACCOUNT_ID=your_admin_mastodon_id
```

### 5.3 마스토돈 OAuth 앱 생성

마스토돈 웹에서:
1. 설정 → 개발 → 새 애플리케이션
2. 애플리케이션 이름: "마녀봇"
3. 리디렉션 URI: `http://localhost:5000/oauth/callback`
4. 스코프: `read write follow`
5. 생성 후 `Client ID`, `Client Secret` 복사

### 5.4 데이터베이스 초기화
```bash
# data 디렉토리 생성
mkdir -p data

# economy.db 초기화
python3 init_db.py data/economy.db
```

---

## 6. Docker로 실행

### 6.1 서비스 구조

```yaml
services:
  web:         # Flask 관리자 웹 (포트 5000)
  celery:      # 비동기 작업 처리
  celery-beat: # 스케줄러 (cron)
  redis:       # 캐시 및 메시지 큐
```

### 6.2 실행
```bash
# 간편 스크립트 사용
./scripts/docker/start.sh

# 또는 직접 실행
docker-compose up -d --build
```

### 6.3 확인
```bash
# 서비스 상태
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f web
```

**접속:**
- 관리자 웹: http://yourserver.duckdns.org:5000

---

## 7. 관리자 웹 설정

### 7.1 Nginx 리버스 프록시

```bash
sudo nano /etc/nginx/sites-available/admin
```

```nginx
server {
    listen 80;
    server_name admin.yourserver.duckdns.org;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 활성화
sudo ln -s /etc/nginx/sites-available/admin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7.2 SSL 인증서

```bash
sudo certbot --nginx -d admin.yourserver.duckdns.org
```

---

## 8. 문제 해결

### 8.1 일반적인 문제

| 문제 | 해결 방법 |
|------|-----------|
| Docker 권한 오류 | `sudo usermod -aG docker $USER && newgrp docker` |
| 포트 충돌 | `docker-compose down && docker-compose up -d` |
| DB 연결 실패 | `.env` 파일의 POSTGRES_* 설정 확인 |
| OAuth 오류 | 리디렉션 URI 확인 |

### 8.2 로그 확인

```bash
# 전체 로그
./scripts/docker/logs.sh

# 실시간 로그
docker-compose logs -f web

# 특정 기간 로그
docker-compose logs --since 30m web
```

### 8.3 재시작

```bash
# 전체 재시작
docker-compose restart

# 특정 서비스만
docker-compose restart web

# 완전 재시작 (데이터 유지)
docker-compose down && docker-compose up -d
```

### 8.4 데이터 백업

```bash
# SQLite 백업
./scripts/docker/backup.sh

# 수동 백업
docker-compose exec web sqlite3 data/economy.db ".backup '/tmp/backup.db'"
docker cp $(docker-compose ps -q web):/tmp/backup.db ./economy_backup.db
```

---

## 📚 추가 문서

- [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - 관리자 웹 사용 가이드
- [ARCHITECTURE.md](ARCHITECTURE.md) - 시스템 아키텍처
- [database.md](database.md) - 데이터베이스 스키마
- [features.md](features.md) - 봇 기능 및 명령어

---

## 🔒 보안 주의사항

**공개 프로젝트 사용 시:**
1. 모든 `.env` 파일을 `.gitignore`에 추가
2. 시크릿 키는 절대 공개 저장소에 커밋하지 마세요
3. 프로덕션 환경에서는 강력한 비밀번호 사용
4. 정기적으로 패키지 업데이트 (`docker-compose pull`)
5. 방화벽 설정 (UFW 등)

---

## 📞 문의

문제가 발생하면 GitHub Issues에 문의하세요:
https://github.com/NinoNinoNinoling/commumanager/issues
