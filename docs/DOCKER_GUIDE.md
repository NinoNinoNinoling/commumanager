# Docker 사용 가이드

마녀봇을 Docker로 실행하는 방법을 설명합니다.

## 📋 목차

- [사전 요구사항](#사전-요구사항)
- [빠른 시작](#빠른-시작)
- [서비스 구조](#서비스-구조)
- [환경 설정](#환경-설정)
- [실행 및 관리](#실행-및-관리)
- [문제 해결](#문제-해결)

---

## 사전 요구사항

### 필수
- Docker 20.10+
- Docker Compose 2.0+

### 설치 확인
```bash
docker --version
docker-compose --version
```

---

## 빠른 시작

### 1. 환경 변수 설정

```bash
# .env.docker를 .env로 복사
cp .env.docker .env

# .env 파일 편집
nano .env
```

**필수 설정 항목:**
```bash
# Mastodon 인스턴스 (예: https://testmast.duckdns.org)
MASTODON_INSTANCE_URL=https://your-instance.social
MASTODON_CLIENT_ID=your-client-id
MASTODON_CLIENT_SECRET=your-client-secret

# 봇 액세스 토큰
BOT_ACCESS_TOKEN=your-bot-token

# PostgreSQL (마스토돈 서버 DB 접속 정보)
# DuckDNS 사용 시: testmast.duckdns.org 또는 서버 IP
POSTGRES_HOST=your-mastodon-server-ip
POSTGRES_PORT=5432
POSTGRES_DB=mastodon_production
POSTGRES_USER=mastodon
POSTGRES_PASSWORD=your-password

# Flask 시크릿 키 (랜덤 문자열 생성)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### 2. 데이터베이스 초기화

```bash
# data 디렉토리 생성
mkdir -p data

# economy.db 초기화
python init_db.py data/economy.db
```

### 3. Docker 실행

```bash
# 간편 스크립트 사용
./scripts/docker/start.sh

# 또는 직접 실행
docker-compose up -d --build
```

### 4. 확인

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
./scripts/docker/logs.sh
```

**접속:**
- 관리자 웹: http://localhost:5000

---

## 서비스 구조

Docker Compose는 5개의 서비스를 실행합니다:

| 서비스 | 설명 | 포트 |
|--------|------|------|
| `web` | Flask 관리자 웹 | 5000 |
| `bot` | 봇 (Streaming API) | - |
| `celery-worker` | Celery 백그라운드 작업 | - |
| `celery-beat` | Celery 스케줄러 (크론) | - |
| `redis` | Redis (캐싱, Celery 브로커) | 6379 |

### 크론 스케줄

Celery Beat가 다음 작업을 자동으로 실행합니다:

- **04:00** - 재화 정산, 활동량 체크, 소셜 분석
- **10:00** - 출석 트윗 발행
- **16:00** - 재화 정산, 활동량 체크

---

## 환경 설정

### 환경 변수 (.env)

`.env` 파일은 Git에 포함되지 않습니다 (보안).

**주요 환경 변수:**

```bash
# Flask
FLASK_ENV=production|development
SECRET_KEY=랜덤_문자열

# 데이터베이스
DATABASE_PATH=/data/economy.db
POSTGRES_HOST=마스토돈_서버_IP
POSTGRES_PORT=5432
POSTGRES_DB=mastodon_production
POSTGRES_USER=mastodon
POSTGRES_PASSWORD=비밀번호

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Mastodon OAuth
MASTODON_INSTANCE_URL=https://your.social
MASTODON_CLIENT_ID=클라이언트_ID
MASTODON_CLIENT_SECRET=클라이언트_시크릿

# 봇 토큰
BOT_ACCESS_TOKEN=봇_액세스_토큰
```

### 데이터 영속성

**볼륨 마운트:**
- `./data` → `/data` (SQLite DB)
- `redis-data` → Redis 데이터

**백업:**
```bash
# economy.db 백업
cp data/economy.db data/economy.db.backup

# 전체 data 디렉토리 백업
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

---

## 실행 및 관리

### 스크립트 사용 (권장)

```bash
# 시작
./scripts/docker/start.sh

# 중지
./scripts/docker/stop.sh

# 재시작 (전체)
./scripts/docker/restart.sh

# 재시작 (특정 서비스)
./scripts/docker/restart.sh web

# 로그 확인 (전체)
./scripts/docker/logs.sh

# 로그 확인 (특정 서비스)
./scripts/docker/logs.sh bot

# 쉘 접속
./scripts/docker/shell.sh web
```

### 직접 명령어 사용

```bash
# 시작
docker-compose up -d

# 중지
docker-compose down

# 재시작
docker-compose restart

# 로그
docker-compose logs -f

# 특정 서비스 재시작
docker-compose restart web

# 특정 서비스 로그
docker-compose logs -f bot

# 쉘 접속
docker-compose exec web /bin/bash
```

### 서비스별 작업

```bash
# Web만 재시작
docker-compose restart web

# Bot만 재시작
docker-compose restart bot

# Celery Worker 재시작
docker-compose restart celery-worker

# Redis 재시작 (주의: 캐시 손실)
docker-compose restart redis
```

---

## 모니터링

### 서비스 상태

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 리소스 사용량
docker stats
```

### 로그 확인

```bash
# 실시간 로그 (전체)
docker-compose logs -f

# 실시간 로그 (Web)
docker-compose logs -f web

# 실시간 로그 (Bot)
docker-compose logs -f bot

# 최근 100줄
docker-compose logs --tail=100

# 특정 시간 이후
docker-compose logs --since="2025-01-01T00:00:00"
```

### 헬스 체크

```bash
# Web 헬스 체크
curl http://localhost:5000/health

# Redis 연결 테스트
docker-compose exec redis redis-cli ping
```

---

## 업데이트

### 코드 업데이트

```bash
# Git pull
git pull origin main

# 재빌드 및 재시작
docker-compose up -d --build
```

### 의존성 업데이트

```bash
# requirements.txt 수정 후
docker-compose build --no-cache
docker-compose up -d
```

---

## 문제 해결

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs

# 특정 서비스 로그
docker-compose logs web

# 상세 로그
docker-compose logs --tail=500
```

### .env 파일 누락

```bash
cp .env.docker .env
nano .env
```

### DB 초기화 실패

```bash
# 기존 DB 백업
mv data/economy.db data/economy.db.old

# 재초기화
python init_db.py data/economy.db
```

### Redis 연결 실패

```bash
# Redis 재시작
docker-compose restart redis

# Redis 로그 확인
docker-compose logs redis
```

### PostgreSQL 연결 실패

**확인 사항:**
1. POSTGRES_HOST가 올바른 IP인지 확인
2. 마스토돈 서버에서 외부 연결 허용 확인
3. 방화벽 설정 확인

```bash
# 컨테이너 내에서 연결 테스트
docker-compose exec web /bin/bash
apt-get update && apt-get install -y postgresql-client
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB
```

### 포트 충돌

**.env 파일 수정:**
```bash
# 기본 5000 → 8000으로 변경
PORT=8000
```

**docker-compose.yml 수정:**
```yaml
web:
  ports:
    - "8000:5000"  # 호스트:컨테이너
```

### 완전 초기화

```bash
# 모든 컨테이너 및 볼륨 삭제
docker-compose down -v

# 이미지 삭제
docker-compose down --rmi all

# 데이터 백업 (선택)
cp -r data data.backup

# 재시작
./scripts/docker/start.sh
```

---

## 프로덕션 배포

### 보안

1. **SECRET_KEY 변경**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **FLASK_ENV 변경**
   ```bash
   FLASK_ENV=production
   ```

3. **방화벽 설정**
   - 5000 포트 외부 접근 제한 (Nginx/Traefik 사용)
   - Redis 포트(6379) 외부 접근 차단

### DuckDNS 도메인 설정

DuckDNS를 사용하는 경우:

**1. DuckDNS 도메인 등록**
- https://www.duckdns.org 접속 후 도메인 생성
- 예: `testmast`, `testadmin`

**2. DuckDNS 업데이트 설정**
```bash
# Crontab에 추가 (5분마다 IP 업데이트)
*/5 * * * * curl "https://www.duckdns.org/update?domains=testmast,testadmin&token=YOUR_TOKEN&ip="
```

**3. 도메인 확인**
```bash
# nslookup으로 도메인 확인
nslookup testmast.duckdns.org
nslookup testadmin.duckdns.org
```

### Nginx 리버스 프록시 예시

**관리자 웹 (testadmin.duckdns.org)**
```nginx
server {
    listen 80;
    server_name testadmin.duckdns.org;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**마스토돈 서버 (testmast.duckdns.org)**
```nginx
server {
    listen 80;
    server_name testmast.duckdns.org;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/TLS (Let's Encrypt)

```bash
# Certbot 설치
sudo apt-get install certbot python3-certbot-nginx

# SSL 인증서 발급 (DuckDNS 도메인)
sudo certbot --nginx -d testadmin.duckdns.org
sudo certbot --nginx -d testmast.duckdns.org

# 자동 갱신 확인
sudo certbot renew --dry-run
```

---

## 참고

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [프로젝트 README](../README.md)
- [관리자 가이드](./ADMIN_GUIDE.md)
