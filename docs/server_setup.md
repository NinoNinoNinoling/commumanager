# 서버 구축 가이드

> **참고**: 이 가이드는 GCP(Google Cloud Platform)와 Oracle Cloud 모두에서 사용할 수 있습니다. 클라우드 제공자별로 차이가 있는 부분은 별도로 표시했습니다.

## 1. 클라우드 인스턴스 생성

### 1-1. GCP (Google Cloud Platform) - 권장

#### VM 인스턴스 생성
1. GCP 콘솔 접속 → **Compute Engine** → **VM 인스턴스**
2. **인스턴스 만들기** 클릭
3. 설정:
   - **이름**: mastodon-server (임의)
   - **리전**: asia-northeast3 (서울) 권장
   - **영역**: asia-northeast3-a
   - **머신 유형**:
     - **시리즈**: E2
     - **머신 유형**: e2-medium (2 vCPU, 4GB 메모리) 이상
     - 또는 **시리즈**: N1, **머신 유형**: n1-standard-2 (2 vCPU, 7.5GB 메모리)
   - **부팅 디스크**:
     - **운영체제**: Ubuntu
     - **버전**: Ubuntu 22.04 LTS
     - **디스크 크기**: 30GB 이상 (50GB 권장)
   - **방화벽**:
     - ✅ HTTP 트래픽 허용
     - ✅ HTTPS 트래픽 허용

#### 고정 외부 IP 주소 예약
1. **VPC 네트워크** → **IP 주소**
2. **외부 고정 주소 예약**
3. 이름 입력 후 생성
4. VM 인스턴스에 할당

#### 방화벽 규칙 설정
1. **VPC 네트워크** → **방화벽**
2. **방화벽 규칙 만들기**
3. SSH 규칙 (자동 생성되어 있음):
   - **대상**: 네트워크의 모든 인스턴스
   - **소스 IP 범위**: 0.0.0.0/0 (또는 자신의 IP만)
   - **프로토콜 및 포트**: tcp:22
4. 추가 규칙 (선택, 개발 서버 접근용):
   - tcp:3000 (Rails)
   - tcp:5000 (Flask)

### 1-2. Oracle Cloud (대안)

#### 인스턴스 스펙
- **Shape**: VM.Standard.A1.Flex (Ampere A1)
- **OCPU**: 4 core
- **Memory**: 24GB RAM
- **Storage**: 100GB
- **OS**: Ubuntu 22.04 LTS

#### 네트워크 설정
```bash
# Security List에 다음 포트 추가
- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)
- 3000 (Rails 개발 서버, 선택)
- 5000 (Flask 개발 서버, 선택)
```

## 2. 기본 패키지 설치

```bash
# SSH 접속 후
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y \
  docker.io \
  docker-compose \
  git \
  nginx \
  certbot \
  python3-certbot-nginx \
  build-essential \
  curl \
  wget

# Docker 사용자 권한 추가
sudo usermod -aG docker $USER
newgrp docker

# 타임존 설정 (한국)
sudo timedatectl set-timezone Asia/Seoul
```

## 3. DuckDNS 도메인 설정

### DuckDNS 가입 및 도메인 등록
1. https://www.duckdns.org 접속
2. GitHub/Google 로그인
3. 서브도메인 생성 (예: `yourserver.duckdns.org`)
4. 토큰 확인

### IP 자동 업데이트 설정
```bash
# DuckDNS 업데이트 스크립트 생성
mkdir -p ~/duckdns
cd ~/duckdns

# 스크립트 작성 (YOUR_DOMAIN과 YOUR_TOKEN을 실제 값으로 교체)
cat > duck.sh << 'EOF'
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=YOUR_DOMAIN&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF

# 실행 권한 부여
chmod +x duck.sh

# 테스트 실행
./duck.sh
cat duck.log  # "OK" 출력 확인

# cron 등록 (5분마다 IP 업데이트)
crontab -e
# 다음 줄 추가:
# */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

## 4. 휘핑 에디션 마스토돈 설치

### 저장소 클론
```bash
cd ~
git clone https://github.com/whippyshou/mastodon.git
cd mastodon
```

### 환경 설정 파일 생성
```bash
# 샘플 파일 복사
cp .env.production.sample .env.production

# 시크릿 키 생성
docker-compose run --rm web bundle exec rake secret
# 출력된 값을 복사 (SECRET_KEY_BASE용)

docker-compose run --rm web bundle exec rake secret
# 출력된 값을 복사 (OTP_SECRET용)

# VAPID 키 생성
docker-compose run --rm web bundle exec rake mastodon:webpush:generate_vapid_key
# 출력된 VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY 복사
```

### .env.production 설정
```bash
nano .env.production
```

**필수 설정 항목:**
```bash
# 도메인
LOCAL_DOMAIN=yourserver.duckdns.org
WEB_DOMAIN=yourserver.duckdns.org

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# PostgreSQL
DB_HOST=db
DB_USER=postgres
DB_NAME=postgres
DB_PASS=postgres  # 변경 권장
DB_PORT=5432

# 시크릿 키 (위에서 생성한 값)
SECRET_KEY_BASE=생성한_시크릿_키_1
OTP_SECRET=생성한_시크릿_키_2

# VAPID 키 (위에서 생성한 값)
VAPID_PRIVATE_KEY=생성한_VAPID_개인키
VAPID_PUBLIC_KEY=생성한_VAPID_공개키

# SMTP 설정 (선택, 메일 발송용)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_LOGIN=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_ADDRESS=notifications@yourserver.duckdns.org

# 로케일
DEFAULT_LOCALE=ko

# 싱글 유저 모드 (폐쇄형 커뮤니티)
SINGLE_USER_MODE=false
LIMITED_FEDERATION_MODE=true
```

### Docker Compose 빌드 및 실행
```bash
# 이미지 빌드 (10~20분 소요)
docker-compose build

# 데이터베이스 초기화
docker-compose run --rm web bundle exec rake db:migrate

# 에셋 프리컴파일
docker-compose run --rm web bundle exec rake assets:precompile

# 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f web
# Ctrl+C로 종료
```

### 관리자 계정 생성
```bash
# 대화형 생성
docker-compose run --rm web bundle exec rake mastodon:setup

# 또는 직접 생성
docker-compose run --rm web bin/tootctl accounts create \
  admin \
  --email admin@example.com \
  --confirmed \
  --role Owner
# 출력된 임시 비밀번호 저장
```

## 5. Nginx 설정

### Nginx 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/mastodon
```

**설정 내용:**
```nginx
map $http_upgrade $connection_upgrade {
  default upgrade;
  ''      close;
}

upstream backend {
    server 127.0.0.1:3000 fail_timeout=0;
}

upstream streaming {
    server 127.0.0.1:4000 fail_timeout=0;
}

proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=CACHE:10m inactive=7d max_size=1g;

server {
  listen 80;
  listen [::]:80;
  server_name yourserver.duckdns.org;
  root /home/ubuntu/mastodon/public;
  location /.well-known/acme-challenge/ { allow all; }
  location / { return 301 https://$host$request_uri; }
}

server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  server_name yourserver.duckdns.org;

  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers HIGH:!MEDIUM:!LOW:!aNULL:!NULL:!SHA;
  ssl_prefer_server_ciphers on;
  ssl_session_cache shared:SSL:10m;
  ssl_session_tickets off;

  # SSL 인증서 (certbot이 자동으로 추가)
  # ssl_certificate /etc/letsencrypt/live/yourserver.duckdns.org/fullchain.pem;
  # ssl_certificate_key /etc/letsencrypt/live/yourserver.duckdns.org/privkey.pem;

  keepalive_timeout 70;
  sendfile on;
  client_max_body_size 80m;

  root /home/ubuntu/mastodon/public;

  gzip on;
  gzip_disable "msie6";
  gzip_vary on;
  gzip_proxied any;
  gzip_comp_level 6;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml image/x-icon;

  location / {
    try_files $uri @proxy;
  }

  location ~ ^/(emoji|packs|system/accounts/avatars|system/media_attachments/files) {
    add_header Cache-Control "public, max-age=31536000, immutable";
    add_header Strict-Transport-Security "max-age=31536000" always;
    try_files $uri @proxy;
  }

  location /sw.js {
    add_header Cache-Control "public, max-age=0";
    add_header Strict-Transport-Security "max-age=31536000" always;
    try_files $uri @proxy;
  }

  location @proxy {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Proxy "";
    proxy_pass_header Server;

    proxy_pass http://backend;
    proxy_buffering on;
    proxy_redirect off;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;

    proxy_cache CACHE;
    proxy_cache_valid 200 7d;
    proxy_cache_valid 410 24h;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    add_header X-Cached $upstream_cache_status;

    tcp_nodelay on;
  }

  location /api/v1/streaming {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Proxy "";

    proxy_pass http://streaming;
    proxy_buffering off;
    proxy_redirect off;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;

    tcp_nodelay on;
  }

  error_page 500 501 502 503 504 /500.html;
}
```

### Nginx 활성화
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/mastodon /etc/nginx/sites-enabled/

# 기본 사이트 비활성화
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

## 6. SSL 인증서 발급 (Let's Encrypt)

```bash
# Certbot으로 SSL 인증서 발급
sudo certbot --nginx -d yourserver.duckdns.org

# 이메일 입력, 약관 동의
# 자동으로 Nginx 설정 업데이트됨

# 자동 갱신 테스트
sudo certbot renew --dry-run

# 자동 갱신은 systemd timer로 자동 설정됨
systemctl list-timers | grep certbot
```

## 7. 접속 확인

### 웹 브라우저 접속
```
https://yourserver.duckdns.org
```

**확인 사항:**
- [ ] HTTPS 접속 성공 (자물쇠 아이콘)
- [ ] 마스토돈 로그인 페이지 표시
- [ ] 관리자 계정 로그인 성공
- [ ] 타임라인 표시

### Docker 컨테이너 상태 확인
```bash
cd ~/mastodon
docker-compose ps

# 모든 컨테이너가 "Up" 상태여야 함
# - db (PostgreSQL)
# - redis
# - web
# - streaming
# - sidekiq
```

### PostgreSQL 접속 확인
```bash
# PostgreSQL 컨테이너 접속
docker-compose exec db psql -U postgres -d postgres

# 테이블 확인
\dt

# 유저 수 확인
SELECT COUNT(*) FROM users;

# 종료
\q
```

## 8. 트러블슈팅

### 컨테이너가 시작되지 않는 경우
```bash
# 로그 확인
docker-compose logs web
docker-compose logs db
docker-compose logs redis

# 컨테이너 재시작
docker-compose restart

# 완전 재시작
docker-compose down
docker-compose up -d
```

### 502 Bad Gateway 오류
```bash
# 백엔드 포트 확인
netstat -tlnp | grep 3000
netstat -tlnp | grep 4000

# web 컨테이너 로그 확인
docker-compose logs -f web

# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log
```

### DB 마이그레이션 오류
```bash
# DB 리셋 (주의: 모든 데이터 삭제)
docker-compose run --rm web bundle exec rake db:reset

# 마이그레이션 재실행
docker-compose run --rm web bundle exec rake db:migrate
```

### 디스크 공간 부족
```bash
# Docker 이미지/컨테이너 정리
docker system prune -a

# 로그 파일 정리
sudo journalctl --vacuum-time=7d
```

## 9. 다음 단계

서버 구축 완료 후:
1. **OAuth 앱 등록**: 관리자 웹용 OAuth 앱 생성
2. **봇 계정 생성**: 재화 지급 봇, 활동량 체크 봇 계정 생성
3. **액세스 토큰 발급**: 봇 API 접근용 토큰 발급
4. **관리 봇 프로젝트 배포**: 이 프로젝트를 서버에 클론하고 설정

상세한 내용은 [로드맵.md](./로드맵.md) 참고

---

## 10. 다중 인스턴스 운영 (테스트 + 본서버)

**권장 사항**: 테스트 서버와 본 서버를 동시에 운영할 경우 **Docker Compose 사용을 강력히 권장**합니다.

### 10-1. 왜 Docker인가?

#### 장점
- ✅ **완벽한 격리**: 테스트/본서버 DB, Redis, 환경변수 완전 분리
- ✅ **포트 관리 간편**: 내부 포트는 동일, 외부 포트만 매핑
- ✅ **프로세스 관리 간단**: `docker-compose up/down` 명령어 하나로 전체 관리
- ✅ **실수 방지**: 테스트 환경에서 실험 시 본서버에 영향 없음
- ✅ **재현 가능**: 같은 설정으로 다른 서버에서도 동일하게 구축 가능

#### Native 설치로 2개 운영 시 문제점
- ❌ PostgreSQL 데이터베이스 2개 수동 관리
- ❌ Redis 인스턴스 2개 (포트 6379, 6380) 수동 설정
- ❌ systemd 서비스 파일 6개+ 작성 필요
- ❌ 포트 충돌 방지를 위한 수동 설정
- ❌ 환경변수 혼동 위험

### 10-2. 디렉토리 구조

```bash
~/mastodon/
├── test/                          # 테스트 서버
│   ├── docker-compose.yml         # 테스트용 Compose 파일
│   ├── .env.production            # 테스트 환경변수
│   └── public/                    # 정적 파일
│
├── prod/                          # 본 서버
│   ├── docker-compose.yml         # 본서버용 Compose 파일
│   ├── .env.production            # 본서버 환경변수
│   └── public/                    # 정적 파일
│
└── shared/                        # 공유 리소스 (선택)
    └── nginx/                     # Nginx 설정
```

### 10-3. 테스트 서버 설정

#### docker-compose.yml (테스트)
```yaml
# ~/mastodon/test/docker-compose.yml
version: '3'
services:
  db:
    restart: always
    image: postgres:14-alpine
    shm_size: 256mb
    networks:
      - mastodon_test_network
    healthcheck:
      test: ['CMD', 'pg_isready', '-U', 'postgres']
    volumes:
      - ./postgres14:/var/lib/postgresql/data
    environment:
      - 'POSTGRES_HOST_AUTH_METHOD=trust'

  redis:
    restart: always
    image: redis:7-alpine
    networks:
      - mastodon_test_network
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
    volumes:
      - ./redis:/data

  web:
    image: ghcr.io/whippyshou/mastodon:latest
    restart: always
    env_file: .env.production
    command: bash -c "rm -f /mastodon/tmp/pids/server.pid; bundle exec rails s -p 3000"
    networks:
      - mastodon_test_network
    healthcheck:
      test: ['CMD-SHELL', 'wget -q --spider --proxy=off localhost:3000/health || exit 1']
    ports:
      - '127.0.0.1:3001:3000'  # 외부 3001 → 내부 3000
    depends_on:
      - db
      - redis
    volumes:
      - ./public/system:/mastodon/public/system

  streaming:
    image: ghcr.io/whippyshou/mastodon:latest
    restart: always
    env_file: .env.production
    command: node ./streaming
    networks:
      - mastodon_test_network
    healthcheck:
      test: ['CMD-SHELL', 'wget -q --spider --proxy=off localhost:4000/api/v1/streaming/health || exit 1']
    ports:
      - '127.0.0.1:4001:4000'  # 외부 4001 → 내부 4000
    depends_on:
      - db
      - redis

  sidekiq:
    image: ghcr.io/whippyshou/mastodon:latest
    restart: always
    env_file: .env.production
    command: bundle exec sidekiq
    depends_on:
      - db
      - redis
    networks:
      - mastodon_test_network
    volumes:
      - ./public/system:/mastodon/public/system
    healthcheck:
      test: ['CMD-SHELL', "ps aux | grep '[s]idekiq\ 6' || false"]

networks:
  mastodon_test_network:
    internal: true
```

#### .env.production (테스트)
```bash
# 도메인
LOCAL_DOMAIN=testserver.duckdns.org
WEB_DOMAIN=testserver.duckdns.org

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# PostgreSQL
DB_HOST=db
DB_USER=postgres
DB_NAME=postgres
DB_PASS=postgres
DB_PORT=5432

# 시크릿 (개별 생성 필요)
SECRET_KEY_BASE=테스트서버_시크릿_1
OTP_SECRET=테스트서버_시크릿_2
VAPID_PRIVATE_KEY=테스트서버_VAPID_개인키
VAPID_PUBLIC_KEY=테스트서버_VAPID_공개키

# 기타
DEFAULT_LOCALE=ko
SINGLE_USER_MODE=false
LIMITED_FEDERATION_MODE=true
```

### 10-4. 본 서버 설정

#### docker-compose.yml (본서버)
```yaml
# ~/mastodon/prod/docker-compose.yml
# 테스트 서버와 거의 동일, 포트만 변경
version: '3'
services:
  db:
    restart: always
    image: postgres:14-alpine
    shm_size: 256mb
    networks:
      - mastodon_prod_network
    healthcheck:
      test: ['CMD', 'pg_isready', '-U', 'postgres']
    volumes:
      - ./postgres14:/var/lib/postgresql/data
    environment:
      - 'POSTGRES_HOST_AUTH_METHOD=trust'

  redis:
    restart: always
    image: redis:7-alpine
    networks:
      - mastodon_prod_network
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
    volumes:
      - ./redis:/data

  web:
    image: ghcr.io/whippyshou/mastodon:latest
    restart: always
    env_file: .env.production
    command: bash -c "rm -f /mastodon/tmp/pids/server.pid; bundle exec rails s -p 3000"
    networks:
      - mastodon_prod_network
    healthcheck:
      test: ['CMD-SHELL', 'wget -q --spider --proxy=off localhost:3000/health || exit 1']
    ports:
      - '127.0.0.1:3000:3000'  # 외부 3000 → 내부 3000
    depends_on:
      - db
      - redis
    volumes:
      - ./public/system:/mastodon/public/system

  streaming:
    image: ghcr.io/whippyshou/mastodon:latest
    restart: always
    env_file: .env.production
    command: node ./streaming
    networks:
      - mastodon_prod_network
    healthcheck:
      test: ['CMD-SHELL', 'wget -q --spider --proxy=off localhost:4000/api/v1/streaming/health || exit 1']
    ports:
      - '127.0.0.1:4000:4000'  # 외부 4000 → 내부 4000
    depends_on:
      - db
      - redis

  sidekiq:
    image: ghcr.io/whippyshou/mastodon:latest
    restart: always
    env_file: .env.production
    command: bundle exec sidekiq
    depends_on:
      - db
      - redis
    networks:
      - mastodon_prod_network
    volumes:
      - ./public/system:/mastodon/public/system
    healthcheck:
      test: ['CMD-SHELL', "ps aux | grep '[s]idekiq\ 6' || false"]

networks:
  mastodon_prod_network:
    internal: true
```

#### .env.production (본서버)
```bash
# 도메인
LOCAL_DOMAIN=mainserver.duckdns.org
WEB_DOMAIN=mainserver.duckdns.org

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# PostgreSQL
DB_HOST=db
DB_USER=postgres
DB_NAME=postgres
DB_PASS=postgres
DB_PORT=5432

# 시크릿 (테스트와 다른 값!)
SECRET_KEY_BASE=본서버_시크릿_1
OTP_SECRET=본서버_시크릿_2
VAPID_PRIVATE_KEY=본서버_VAPID_개인키
VAPID_PUBLIC_KEY=본서버_VAPID_공개키

# 기타
DEFAULT_LOCALE=ko
SINGLE_USER_MODE=false
LIMITED_FEDERATION_MODE=true
```

### 10-5. DuckDNS 설정 (2개 도메인)

#### 서브도메인 2개 생성
1. https://www.duckdns.org 접속
2. `testserver` 서브도메인 생성 → 서버 IP 입력
3. `mainserver` 서브도메인 생성 → 동일한 서버 IP 입력

#### IP 자동 업데이트 스크립트 수정
```bash
# ~/duckdns/duck.sh
#!/bin/bash
# 2개 도메인 동시 업데이트
echo url="https://www.duckdns.org/update?domains=testserver,mainserver&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

### 10-6. Nginx 설정 (2개 도메인)

#### /etc/nginx/sites-available/mastodon-test
```nginx
map $http_upgrade $connection_upgrade {
  default upgrade;
  ''      close;
}

upstream backend_test {
    server 127.0.0.1:3001 fail_timeout=0;
}

upstream streaming_test {
    server 127.0.0.1:4001 fail_timeout=0;
}

proxy_cache_path /var/cache/nginx/test levels=1:2 keys_zone=CACHE_TEST:10m inactive=7d max_size=1g;

server {
  listen 80;
  listen [::]:80;
  server_name testserver.duckdns.org;
  root /home/ubuntu/mastodon/test/public;
  location /.well-known/acme-challenge/ { allow all; }
  location / { return 301 https://$host$request_uri; }
}

server {
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  server_name testserver.duckdns.org;

  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers HIGH:!MEDIUM:!LOW:!aNULL:!NULL:!SHA;
  ssl_prefer_server_ciphers on;
  ssl_session_cache shared:SSL:10m;
  ssl_session_tickets off;

  # SSL 인증서 (certbot이 자동으로 추가)
  # ssl_certificate /etc/letsencrypt/live/testserver.duckdns.org/fullchain.pem;
  # ssl_certificate_key /etc/letsencrypt/live/testserver.duckdns.org/privkey.pem;

  keepalive_timeout 70;
  sendfile on;
  client_max_body_size 80m;

  root /home/ubuntu/mastodon/test/public;

  gzip on;
  gzip_disable "msie6";
  gzip_vary on;
  gzip_proxied any;
  gzip_comp_level 6;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml image/x-icon;

  location / {
    try_files $uri @proxy;
  }

  location ~ ^/(emoji|packs|system/accounts/avatars|system/media_attachments/files) {
    add_header Cache-Control "public, max-age=31536000, immutable";
    add_header Strict-Transport-Security "max-age=31536000" always;
    try_files $uri @proxy;
  }

  location /sw.js {
    add_header Cache-Control "public, max-age=0";
    add_header Strict-Transport-Security "max-age=31536000" always;
    try_files $uri @proxy;
  }

  location @proxy {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Proxy "";
    proxy_pass_header Server;

    proxy_pass http://backend_test;
    proxy_buffering on;
    proxy_redirect off;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;

    proxy_cache CACHE_TEST;
    proxy_cache_valid 200 7d;
    proxy_cache_valid 410 24h;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    add_header X-Cached $upstream_cache_status;

    tcp_nodelay on;
  }

  location /api/v1/streaming {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Proxy "";

    proxy_pass http://streaming_test;
    proxy_buffering off;
    proxy_redirect off;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;

    tcp_nodelay on;
  }

  error_page 500 501 502 503 504 /500.html;
}
```

#### /etc/nginx/sites-available/mastodon-prod
```nginx
# 테스트 서버와 유사, 다음만 변경:
# - server_name: mainserver.duckdns.org
# - upstream backend_prod: 127.0.0.1:3000
# - upstream streaming_prod: 127.0.0.1:4000
# - proxy_cache_path: CACHE_PROD
# - root: /home/ubuntu/mastodon/prod/public
# - SSL 인증서 경로: mainserver.duckdns.org

# (위 테스트 서버 설정을 복사 후 위 항목들만 변경)
```

#### Nginx 활성화
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/mastodon-test /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/mastodon-prod /etc/nginx/sites-enabled/

# 기본 사이트 비활성화 (아직 안 했다면)
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

### 10-7. SSL 인증서 발급 (2개 도메인)

```bash
# 테스트 서버
sudo certbot --nginx -d testserver.duckdns.org

# 본 서버
sudo certbot --nginx -d mainserver.duckdns.org

# 자동 갱신 확인
sudo certbot renew --dry-run
```

### 10-8. 서버 시작 및 관리

#### 테스트 서버
```bash
cd ~/mastodon/test

# 시크릿 키 생성
docker run --rm -it ghcr.io/whippyshou/mastodon:latest bundle exec rake secret
# → SECRET_KEY_BASE

docker run --rm -it ghcr.io/whippyshou/mastodon:latest bundle exec rake secret
# → OTP_SECRET

docker run --rm -it ghcr.io/whippyshou/mastodon:latest bundle exec rake mastodon:webpush:generate_vapid_key
# → VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY

# .env.production 파일 편집 (위에서 생성한 값 입력)
nano .env.production

# DB 마이그레이션
docker-compose run --rm web bundle exec rake db:migrate

# 에셋 프리컴파일
docker-compose run --rm web bundle exec rake assets:precompile

# 컨테이너 시작
docker-compose up -d

# 관리자 계정 생성
docker-compose run --rm web bin/tootctl accounts create \
  test_admin \
  --email test@example.com \
  --confirmed \
  --role Owner

# 로그 확인
docker-compose logs -f web
```

#### 본 서버
```bash
cd ~/mastodon/prod

# 동일한 과정 반복 (시크릿 키는 테스트와 다르게!)
# ...
```

#### 관리 명령어
```bash
# 테스트 서버 중지
cd ~/mastodon/test && docker-compose down

# 테스트 서버 시작
cd ~/mastodon/test && docker-compose up -d

# 본 서버 재시작
cd ~/mastodon/prod && docker-compose restart

# 테스트 서버 로그
cd ~/mastodon/test && docker-compose logs -f web

# 본 서버 DB 백업
cd ~/mastodon/prod && docker-compose exec db pg_dump -U postgres postgres > backup.sql

# 두 서버 상태 확인
docker ps
```

### 10-9. 포트 요약

| 서비스 | 테스트 (내부→외부) | 본서버 (내부→외부) |
|--------|-------------------|-------------------|
| Web | 3000 → 3001 | 3000 → 3000 |
| Streaming | 4000 → 4001 | 4000 → 4000 |
| PostgreSQL | 5432 (컨테이너 내부) | 5432 (컨테이너 내부) |
| Redis | 6379 (컨테이너 내부) | 6379 (컨테이너 내부) |

---

## 11. VSCode SSH 연결 문제 해결

VSCode Remote SSH로 서버 접속 시 방화벽 문제로 연결이 실패하는 경우 해결 방법입니다.

### 11-1. 클라우드 제공자별 방화벽 설정

#### GCP 방화벽 설정

1. GCP 콘솔 → **VPC 네트워크** → **방화벽**
2. SSH 규칙 확인 (보통 자동 생성됨):
   - 이름: `default-allow-ssh` 또는 유사한 이름
   - 대상: 네트워크의 모든 인스턴스
   - 소스 IP 범위: `0.0.0.0/0`
   - 프로토콜 및 포트: `tcp:22`
3. 규칙이 없다면 **방화벽 규칙 만들기**:
   - **이름**: allow-ssh
   - **트래픽 방향**: 수신
   - **일치 시 작업**: 허용
   - **대상**: 네트워크의 모든 인스턴스
   - **소스 필터**: IPv4 범위
   - **소스 IPv4 범위**: `0.0.0.0/0` (또는 `YOUR_HOME_IP/32`)
   - **프로토콜 및 포트**: tcp:22
4. **만들기** 클릭

#### 보안 강화 옵션 (선택)
```bash
# 집 IP만 허용 (권장)
Source IPv4 범위: 123.456.789.012/32  # 자신의 집 공인 IP

# IP 확인 방법
curl ifconfig.me
```

#### Oracle Cloud 방화벽 설정

1. Oracle Cloud 콘솔 로그인
2. **Compute → Instances** → 인스턴스 선택
3. **Subnet** 클릭 → **Security Lists** 클릭
4. **Default Security List** 클릭
5. **Add Ingress Rules** 클릭
6. 다음 정보 입력:
   - **Source Type**: CIDR
   - **Source CIDR**: `0.0.0.0/0` (모든 IP 허용) 또는 `YOUR_HOME_IP/32` (집 IP만)
   - **IP Protocol**: TCP
   - **Destination Port Range**: `22`
   - **Description**: SSH for VSCode
7. **Add Ingress Rules** 클릭

### 11-2. 인스턴스 내부 방화벽 설정

#### Ubuntu 방화벽 (ufw) 확인
```bash
# SSH로 서버 접속 후
sudo ufw status

# 만약 active 상태면
sudo ufw allow 22/tcp
sudo ufw reload
```

#### iptables 확인 (ufw가 비활성화된 경우)
```bash
# 현재 규칙 확인
sudo iptables -L -n -v

# SSH 허용 규칙 추가 (필요시)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --sport 22 -j ACCEPT

# 규칙 저장
sudo netfilter-persistent save
```

### 11-3. VSCode SSH 설정

#### ~/.ssh/config 파일 예시
```bash
# Windows: C:\Users\YourName\.ssh\config
# Mac/Linux: ~/.ssh/config

Host oracle-server
    HostName your-server-ip-or-domain
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/your-private-key
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
```

#### SSH 키 권한 설정
```bash
# Mac/Linux
chmod 600 ~/.ssh/your-private-key
chmod 644 ~/.ssh/config

# Windows (PowerShell 관리자 권한)
icacls C:\Users\YourName\.ssh\your-private-key /inheritance:r
icacls C:\Users\YourName\.ssh\your-private-key /grant:r "%USERNAME%:R"
```

### 11-4. 연결 테스트

#### 터미널에서 직접 연결
```bash
# Mac/Linux
ssh -i ~/.ssh/your-private-key ubuntu@your-server-ip -v

# Windows (PowerShell)
ssh -i C:\Users\YourName\.ssh\your-private-key ubuntu@your-server-ip -v

# -v 옵션으로 상세 로그 확인
# 연결 성공하면 VSCode도 성공할 가능성 높음
```

#### VSCode 연결
1. VSCode에서 `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)
2. `Remote-SSH: Connect to Host...` 선택
3. 설정한 호스트 이름 선택 (예: `oracle-server`)
4. 연결 시도

### 11-5. 문제 해결

#### 연결 시간 초과 (Timeout)
```bash
# Oracle Cloud 방화벽 규칙 재확인
# 또는 집 공유기 방화벽 설정 확인

# 대안: SSH 터널링 (포트 포워딩)
ssh -L 2222:localhost:22 ubuntu@your-server-ip
# 그 다음 VSCode에서 localhost:2222로 연결
```

#### 권한 거부 (Permission Denied)
```bash
# SSH 키 파일 권한 확인
ls -l ~/.ssh/your-private-key
# -rw------- 이어야 함 (600)

# 올바른 키 파일인지 확인
ssh-keygen -lf ~/.ssh/your-private-key
```

#### "Could not establish connection" 오류
```bash
# VSCode 서버 재설치
# VSCode에서 Ctrl+Shift+P → "Remote-SSH: Kill VS Code Server on Host"
# 그 다음 다시 연결 시도
```

#### 방화벽 로그 확인
```bash
# 서버에서 실시간 로그 확인
sudo tail -f /var/log/auth.log

# 연결 시도가 서버까지 도달하는지 확인
# 도달한다면 Oracle Cloud 방화벽은 OK
# 도달하지 않는다면 Oracle Cloud 방화벽 문제
```

---

## 12. Native 설치에서 Docker로 마이그레이션

이미 Native 방식 (Ruby 직접 설치)으로 마스토돈을 설치한 경우, Docker로 전환하는 방법입니다.

### 12-1. 마이그레이션 전 준비

#### 데이터 백업
```bash
# PostgreSQL 데이터베이스 백업
sudo -u postgres pg_dump mastodon_production > ~/mastodon_backup_$(date +%Y%m%d).sql

# 환경 변수 백업
cp ~/.env.production ~/env_backup_$(date +%Y%m%d)

# 미디어 파일 백업 (선택)
tar -czf ~/media_backup_$(date +%Y%m%d).tar.gz /path/to/mastodon/public/system

# 백업 파일 확인
ls -lh ~/*backup*
```

#### 현재 서비스 중지
```bash
# systemd 서비스 중지 (사용 중인 경우)
sudo systemctl stop mastodon-web
sudo systemctl stop mastodon-sidekiq
sudo systemctl stop mastodon-streaming

# 또는 수동 프로세스 중지
pkill -f "rails server"
pkill -f "sidekiq"
pkill -f "node ./streaming"
```

### 12-2. Docker 환경 준비

#### 디렉토리 구조 생성
```bash
mkdir -p ~/mastodon/prod
cd ~/mastodon/prod
```

#### docker-compose.yml 생성
```bash
# 위 10-4 섹션의 docker-compose.yml 내용 사용
nano docker-compose.yml
```

#### .env.production 복사 및 수정
```bash
# 기존 환경변수 파일 복사
cp ~/old-mastodon/.env.production ~/mastodon/prod/.env.production

# DB 연결 정보 수정 (Docker용으로)
nano ~/mastodon/prod/.env.production
```

**수정해야 할 항목:**
```bash
# 변경 전 (Native)
DB_HOST=localhost
REDIS_HOST=localhost

# 변경 후 (Docker)
DB_HOST=db
REDIS_HOST=redis
```

### 12-3. 데이터 마이그레이션

#### PostgreSQL 데이터 복원
```bash
cd ~/mastodon/prod

# 컨테이너 시작 (DB만)
docker-compose up -d db

# 잠시 대기 (DB 초기화 완료까지)
sleep 10

# 백업 파일 복원
docker-compose exec -T db psql -U postgres postgres < ~/mastodon_backup_*.sql

# 복원 확인
docker-compose exec db psql -U postgres postgres -c "SELECT COUNT(*) FROM users;"
```

#### 미디어 파일 복사 (선택)
```bash
# public/system 디렉토리 생성
mkdir -p ~/mastodon/prod/public/system

# 기존 미디어 파일 복사
cp -r /path/to/old-mastodon/public/system/* ~/mastodon/prod/public/system/

# 권한 설정
chmod -R 755 ~/mastodon/prod/public/system
```

### 12-4. Docker 컨테이너 시작

```bash
cd ~/mastodon/prod

# DB 마이그레이션 (새로운 테이블 구조 적용)
docker-compose run --rm web bundle exec rake db:migrate

# 에셋 프리컴파일
docker-compose run --rm web bundle exec rake assets:precompile

# 모든 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f web
```

### 12-5. Nginx 설정 변경

#### 기존 설정 백업
```bash
sudo cp /etc/nginx/sites-available/mastodon /etc/nginx/sites-available/mastodon.native.bak
```

#### Nginx 설정 수정
```bash
sudo nano /etc/nginx/sites-available/mastodon
```

**변경 사항:**
```nginx
# 변경 전 (Native, 포트가 다를 수 있음)
upstream backend {
    server 127.0.0.1:3000 fail_timeout=0;
}

# root 경로
root /home/ubuntu/old-mastodon/public;

# 변경 후 (Docker)
upstream backend {
    server 127.0.0.1:3000 fail_timeout=0;  # 동일 (Docker가 3000으로 매핑)
}

# root 경로
root /home/ubuntu/mastodon/prod/public;
```

#### Nginx 재시작
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 12-6. 동작 확인

```bash
# 웹 브라우저에서 접속
https://yourserver.duckdns.org

# 로그인 테스트
# 타임라인 확인
# 미디어 업로드 테스트

# Docker 컨테이너 상태 확인
docker-compose ps

# 모든 컨테이너가 "Up" 상태여야 함
```

### 12-7. Native 설치 정리 (선택)

**주의**: 완벽하게 동작 확인 후에만 진행!

```bash
# systemd 서비스 비활성화
sudo systemctl disable mastodon-web
sudo systemctl disable mastodon-sidekiq
sudo systemctl disable mastodon-streaming

# 서비스 파일 삭제 (선택)
sudo rm /etc/systemd/system/mastodon-*.service
sudo systemctl daemon-reload

# Native PostgreSQL/Redis 중지 (다른 용도로 사용 안 한다면)
sudo systemctl stop postgresql
sudo systemctl stop redis-server
sudo systemctl disable postgresql
sudo systemctl disable redis-server

# Ruby/Node 환경 정리 (선택, 신중히)
# rbenv, nvm 등 설치한 것들

# 기존 디렉토리 보관 (당분간)
mv ~/old-mastodon ~/old-mastodon.backup
# 몇 주 후 문제 없으면 삭제
# rm -rf ~/old-mastodon.backup
```

### 12-8. 마이그레이션 체크리스트

- [ ] PostgreSQL 백업 완료
- [ ] .env.production 백업 완료
- [ ] 미디어 파일 백업 (선택)
- [ ] Native 서비스 중지
- [ ] Docker 환경 구축 (.env 수정 포함)
- [ ] DB 데이터 복원
- [ ] Docker 컨테이너 시작
- [ ] Nginx 설정 변경
- [ ] HTTPS 접속 확인
- [ ] 로그인 테스트 성공
- [ ] 타임라인 정상 작동
- [ ] 미디어 업로드 테스트
- [ ] 최소 1주일 안정성 확인 후 Native 환경 정리
