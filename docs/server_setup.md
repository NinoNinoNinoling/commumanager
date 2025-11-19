# 서버 구축 가이드

## 1. 클라우드 인스턴스 생성

### GCP
- 리전: asia-northeast3 (서울)
- 머신: E2 e2-medium (2 vCPU, 4GB) 이상
- OS: Ubuntu 22.04 LTS
- 디스크: 30GB 이상
- 방화벽: HTTP/HTTPS 허용
- 고정 IP 예약 및 할당

## 2. 기본 패키지 설치

```bash
sudo apt update && sudo apt upgrade -y

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

sudo usermod -aG docker $USER
newgrp docker

sudo timedatectl set-timezone Asia/Seoul
```

## 3. DuckDNS 도메인 설정

### 도메인 등록
1. https://www.duckdns.org 로그인
2. 서브도메인 생성
3. 서버 IP 입력

### IP 자동 업데이트
```bash
mkdir -p ~/duckdns && cd ~/duckdns

cat > duck.sh << 'EOF'
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=YOUR_DOMAIN&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF

chmod +x duck.sh
./duck.sh
cat duck.log  # "OK" 확인

crontab -e
# 추가: */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

## 4. 휘핑 에디션 마스토돈 설치

### 저장소 클론
```bash
cd ~
git clone https://github.com/whippyshou/mastodon.git
cd mastodon
```

### 시크릿 키 생성
```bash
cp .env.production.sample .env.production

docker-compose run --rm web bundle exec rake secret  # SECRET_KEY_BASE
docker-compose run --rm web bundle exec rake secret  # OTP_SECRET
docker-compose run --rm web bundle exec rake mastodon:webpush:generate_vapid_key
```

### .env.production 설정
```bash
nano .env.production
```

**필수 설정:**
```bash
LOCAL_DOMAIN=yourserver.duckdns.org
WEB_DOMAIN=yourserver.duckdns.org

REDIS_HOST=redis
REDIS_PORT=6379

DB_HOST=db
DB_USER=postgres
DB_NAME=postgres
DB_PASS=postgres
DB_PORT=5432

SECRET_KEY_BASE=생성한_시크릿_키_1
OTP_SECRET=생성한_시크릿_키_2
VAPID_PRIVATE_KEY=생성한_VAPID_개인키
VAPID_PUBLIC_KEY=생성한_VAPID_공개키

DEFAULT_LOCALE=ko
SINGLE_USER_MODE=false
LIMITED_FEDERATION_MODE=true
```

### 빌드 및 실행
```bash
docker-compose build
docker-compose run --rm web bundle exec rake db:migrate
docker-compose run --rm web bundle exec rake assets:precompile
docker-compose up -d

docker-compose logs -f web  # Ctrl+C 종료
```

### 관리자 계정 생성
```bash
docker-compose run --rm web bin/tootctl accounts create \
  admin \
  --email admin@example.com \
  --confirmed \
  --role Owner
```

## 5. Nginx 설정

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
sudo ln -s /etc/nginx/sites-available/mastodon /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## 6. SSL 인증서 발급

```bash
sudo certbot --nginx -d yourserver.duckdns.org
sudo certbot renew --dry-run  # 자동 갱신 테스트
```

## 7. 접속 확인

```
https://yourserver.duckdns.org
```

**체크리스트:**
- HTTPS 접속 성공
- 로그인 페이지 표시
- 관리자 로그인 성공
- 타임라인 표시

### 컨테이너 상태 확인
```bash
docker-compose ps  # 모두 "Up" 상태
```

### PostgreSQL 접속
```bash
docker-compose exec db psql -U postgres -d postgres
\dt
SELECT COUNT(*) FROM users;
\q
```

## 8. 트러블슈팅

### 컨테이너 시작 실패
```bash
docker-compose logs web
docker-compose restart
docker-compose down && docker-compose up -d
```

### 502 Bad Gateway
```bash
netstat -tlnp | grep 3000
docker-compose logs -f web
sudo tail -f /var/log/nginx/error.log
```

### DB 마이그레이션 오류
```bash
docker-compose run --rm web bundle exec rake db:reset
docker-compose run --rm web bundle exec rake db:migrate
```

### 디스크 공간 부족
```bash
docker system prune -a
sudo journalctl --vacuum-time=7d
```

## 9. 다중 인스턴스 운영 (테스트 + 본서버)

### 디렉토리 구조
```bash
~/mastodon/
├── test/
│   ├── docker-compose.yml
│   ├── .env.production
│   └── public/
└── prod/
    ├── docker-compose.yml
    ├── .env.production
    └── public/
```

### 테스트 서버 docker-compose.yml
```yaml
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
      - '127.0.0.1:3001:3000'
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
      - '127.0.0.1:4001:4000'
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

### 본서버 포트 (3000, 4000)
테스트 서버와 동일한 구조, 포트만 변경:
- web: `127.0.0.1:3000:3000`
- streaming: `127.0.0.1:4000:4000`
- network: `mastodon_prod_network`

### DuckDNS 2개 도메인
```bash
# duck.sh
echo url="https://www.duckdns.org/update?domains=testserver,mainserver&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

### Nginx 설정 (2개 도메인)
각 도메인별 설정 파일 생성:
- `/etc/nginx/sites-available/mastodon-test` (포트 3001, 4001)
- `/etc/nginx/sites-available/mastodon-prod` (포트 3000, 4000)

```bash
sudo ln -s /etc/nginx/sites-available/mastodon-test /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/mastodon-prod /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### SSL 인증서
```bash
sudo certbot --nginx -d testserver.duckdns.org
sudo certbot --nginx -d mainserver.duckdns.org
```

### 관리 명령어
```bash
cd ~/mastodon/test && docker-compose up -d    # 테스트 시작
cd ~/mastodon/prod && docker-compose up -d    # 본서버 시작
cd ~/mastodon/test && docker-compose down     # 테스트 중지
docker ps                                      # 전체 상태 확인
```

## 10. VSCode SSH 연결

### GCP 방화벽
1. VPC 네트워크 → 방화벽
2. SSH 규칙 확인 (tcp:22 허용)

### Ubuntu 방화벽
```bash
sudo ufw status
sudo ufw allow 22/tcp
sudo ufw reload
```

### ~/.ssh/config
```bash
Host gcp-server
    HostName your-server-ip
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/your-key
    ServerAliveInterval 60
```

### 연결 테스트
```bash
ssh -i ~/.ssh/your-key ubuntu@your-server-ip -v
```

## 11. Native → Docker 마이그레이션

### 백업
```bash
sudo -u postgres pg_dump mastodon_production > ~/mastodon_backup_$(date +%Y%m%d).sql
cp ~/.env.production ~/env_backup_$(date +%Y%m%d)
tar -czf ~/media_backup_$(date +%Y%m%d).tar.gz /path/to/mastodon/public/system
```

### 현재 서비스 중지
```bash
sudo systemctl stop mastodon-web mastodon-sidekiq mastodon-streaming
```

### Docker 환경 준비
```bash
mkdir -p ~/mastodon/prod && cd ~/mastodon/prod
# docker-compose.yml 생성 (섹션 9 참고)
cp ~/old-mastodon/.env.production .env.production
nano .env.production  # DB_HOST=db, REDIS_HOST=redis로 변경
```

### 데이터 복원
```bash
docker-compose up -d db
sleep 10
docker-compose exec -T db psql -U postgres postgres < ~/mastodon_backup_*.sql
docker-compose exec db psql -U postgres postgres -c "SELECT COUNT(*) FROM users;"
```

### 컨테이너 시작
```bash
docker-compose run --rm web bundle exec rake db:migrate
docker-compose run --rm web bundle exec rake assets:precompile
docker-compose up -d
```

### Nginx 수정
```bash
sudo nano /etc/nginx/sites-available/mastodon
# root 경로를 ~/mastodon/prod/public로 변경
sudo nginx -t && sudo systemctl restart nginx
```

### Native 환경 정리
```bash
sudo systemctl disable mastodon-web mastodon-sidekiq mastodon-streaming
sudo systemctl stop postgresql redis-server
sudo systemctl disable postgresql redis-server
mv ~/old-mastodon ~/old-mastodon.backup
```

## 다음 단계

1. OAuth 앱 등록 (관리자 웹용)
2. 봇 계정 생성 (재화 지급 봇, 활동량 체크 봇)
3. 액세스 토큰 발급
4. 관리 봇 프로젝트 배포

상세: [로드맵.md](./로드맵.md)
