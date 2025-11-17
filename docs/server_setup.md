# 서버 구축 가이드

## 1. Oracle Cloud 인스턴스 생성

### 인스턴스 스펙
- **Shape**: VM.Standard.A1.Flex (Ampere A1)
- **OCPU**: 4 core
- **Memory**: 24GB RAM
- **Storage**: 100GB
- **OS**: Ubuntu 22.04 LTS

### 네트워크 설정
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
