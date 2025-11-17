# Part 2: 기술 스택 및 인프라

---

## 1. 서버 인프라

### 1.1 오라클 클라우드 (1순위 추천)

**Oracle Cloud Infrastructure (OCI) - Always Free Tier**

**선택 이유**:
- ✅ **완전 무료** (평생 프리 티어)
- ✅ **고성능**: Ampere A1 (4 OCPU, 24GB RAM)
- ✅ **한국 리전**: 춘천 (ap-chuncheon-1)
- ✅ **빠른 속도**: 국내 사용자에게 최적
- ✅ **충분한 성능**: 50~100명 가능
- ✅ **스토리지**: 200GB Block Volume

**스펙 상세**:
```
CPU: ARM64 Ampere A1 (4 OCPU)
RAM: 24GB
Storage: 200GB (Boot Volume + Block Volume)
Network: 10TB/월 아웃바운드
리전: 춘천 (ap-chuncheon-1)
OS: Ubuntu 22.04 LTS
```

**현재 상태**: 카드 인증 문제로 계정 생성 진행 중

**해결 방법**:
- 해외 체크카드 시도
- 선불카드 시도
- 다른 팀원 명의로 시도

---

### 1.2 대안 호스팅 (유료)

#### Hetzner Cloud
```
가격: 월 €4.5 (약 6,500원)
CPU: 2 vCPU (AMD/Intel)
RAM: 4GB
Storage: 40GB SSD
위치: 독일 또는 핀란드
단점: 한국에서 느림 (지연 200~300ms)
```

#### Contabo
```
가격: 월 €6.99 (약 10,000원)
CPU: 6 vCPU
RAM: 16GB
Storage: 400GB SSD
위치: 독일 또는 미국
단점: 한국에서 느림
```

**결론**: 오라클 계정 생성 성공 시까지 대기, 최종 실패 시 Hetzner 사용

---

## 2. 기술 스택

### 2.1 마스토돈 서버 (휘핑 에디션)

```yaml
베이스: 마스토돈 v4.2.1
언어: Ruby 3.2.2
프레임워크: Ruby on Rails
프론트엔드: React.js + Redux
스트리밍: Node.js 16.20.2
데이터베이스: PostgreSQL 12.16+
캐시/큐: Redis 5.0.7+
```

---

### 2.2 경제 시스템 봇

```yaml
언어: Python 3.9+
라이브러리:
  - Mastodon.py (마스토돈 API)
  - psycopg2 (PostgreSQL 연결)
  - sqlite3 (내장)
서비스 관리: systemd
스케줄링: cron
```

**주요 모듈**:
```
economy_bot/
├── reward_bot.py          # 실시간 재화 지급
├── activity_checker.py    # 활동량 체크 (벌크)
├── command_handler.py     # 봇 명령어 처리
├── game_engine.py         # 게임 로직 (추후)
├── database.py            # DB 유틸리티
└── config.py              # 설정 로드
```

---

### 2.3 관리자 웹

```yaml
프레임워크: Flask 3.x
템플릿: Jinja2
UI: Bootstrap 5 (기본 스타일만)
차트: Chart.js (통계용)
인증: Mastodon OAuth
```

**특징**:
- 최소 디자인 (Bootstrap 기본)
- 기능 중심
- 모바일 대응 후순위

---

### 2.4 데이터베이스 전략

#### PostgreSQL (마스토돈 기존 DB)
**용도**: 읽기 전용 참조
- 유저 계정 정보
- 답글/툿 데이터
- 마스토돈 원본 데이터

**접근 방식**:
```python
# 읽기 전용으로만 접근
conn = psycopg2.connect(
    dbname="mastodon_production",
    user="mastodon",
    password="...",
    host="localhost",
    options="-c default_transaction_read_only=on"
)
```

#### SQLite (경제 시스템 전용)
**용도**: 경제 데이터 독립 관리
- 재화, 거래 기록
- 경고 로그
- 휴식 기간
- 상점 아이템
- 시스템 설정

**파일 위치**: `/home/ubuntu/economy_bot/economy.db`

**장점**:
- 마스토돈 DB와 분리 (안전)
- 백업 간편 (파일 하나)
- 30~50명 규모 충분
- 별도 DB 서버 불필요

---

## 3. 인프라 구성

### 3.1 네트워크 구성

```
Internet
   │
   ▼
[DuckDNS]  yourserver.duckdns.org (무료 도메인)
   │
   ▼
[Cloudflare/Let's Encrypt SSL]
   │
   ▼
[Nginx - 리버스 프록시]
   ├──→ Mastodon Web (Port 3000)
   ├──→ Mastodon Streaming (Port 4000)
   └──→ Admin Web (Port 5000)
```

**포트 설정**:
```
22:  SSH
80:  HTTP (자동으로 443 리다이렉트)
443: HTTPS
3000: Mastodon Web (내부)
4000: Mastodon Streaming (내부)
5000: Admin Web (내부)
```

---

### 3.2 도메인 및 SSL

#### 도메인: DuckDNS (무료)
```
URL: https://www.duckdns.org
방식: DDNS (Dynamic DNS)
예시: yourserver.duckdns.org
갱신: 자동 (크론)
```

**설정**:
```bash
# 크론으로 5분마다 IP 갱신
*/5 * * * * curl "https://www.duckdns.org/update?domains=yourserver&token=YOUR_TOKEN"
```

#### SSL: Let's Encrypt (무료)
```
발급: Certbot
갱신: 자동 (certbot renew)
유효기간: 90일 (자동 갱신)
```

---

### 3.3 SMTP (이메일 발송)

**SendGrid 무료 플랜**
```
가격: 무료
한도: 월 100통
용도:
  - 가입 인증
  - 비밀번호 찾기
  - (선택) 관리자 알림
```

**대안**: Brevo (구 Sendinblue) - 월 300통 무료

---

## 4. 성능 최적화 전략

### 4.1 마스토돈 최적화

**Docker 설정** (.env.production):
```bash
WEB_CONCURRENCY=4          # 4-core에 맞춤
MAX_THREADS=5
STREAMING_CLUSTER_NUM=1
DB_POOL=25
```

**Redis 캐싱**:
- 타임라인 캐싱
- 세션 저장
- Sidekiq 큐

---

### 4.2 경제 봇 최적화

**벌크 처리 전략**:
```python
# 오전 5시 - 심야 시간 활용
# PostgreSQL 한 번에 쿼리
query = """
SELECT 
    u.id, u.username,
    COUNT(s.id) as reply_count
FROM accounts u
LEFT JOIN statuses s ON ...
WHERE s.created_at > NOW() - INTERVAL '48 hours'
GROUP BY u.id
"""

# 매시간 30명씩 조회 (720회/일)
# → 하루 2번 벌크 조회 (2회/일)
# 360배 감소!
```

**크론 스케줄**:
```bash
# 오전 5시 - 무거운 벌크 처리
0 5 * * * python3 /path/to/bulk_activity_check.py

# 오후 12시 - 중간 체크
0 12 * * * python3 /path/to/activity_check.py
```

---

### 4.3 백업 전략

**자동 백업 (크론)**:
```bash
# 매일 새벽 3시 - SQLite 백업
0 3 * * * sqlite3 /path/to/economy.db ".backup '/backups/economy_$(date +\%Y\%m\%d).db'"

# 주 1회 일요일 - PostgreSQL 백업
0 4 * * 0 docker exec mastodon_db_1 pg_dump -Fc -U postgres mastodon_production > /backups/mastodon_$(date +\%Y\%m\%d).dump

# 주 1회 - 미디어 파일 백업
0 5 * * 0 tar -czf /backups/media_$(date +\%Y\%m\%d).tar.gz /path/to/mastodon/public/system

# 30일 지난 백업 자동 삭제
0 6 * * 0 find /backups -name "*.db" -mtime +30 -delete
```

**백업 저장 위치**:
- 로컬: `/home/ubuntu/backups`
- (선택) 클라우드: Oracle Object Storage (무료)

---

## 5. 보안 설정

### 5.1 방화벽 (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

### 5.2 파일 권한

```bash
# SQLite DB 권한
chmod 600 /path/to/economy.db
chown ubuntu:ubuntu /path/to/economy.db

# 환경 변수 파일 (사용 안 함)
# .env 파일 불필요 (DB에 설정 저장)
```

---

### 5.3 OAuth 보안

**마스토돈 OAuth**:
- 관리자 웹은 OAuth만 허용
- 비밀번호 직접 입력 없음
- 권한 체크: Owner/Admin만 접근

---

## 6. 모니터링

### 6.1 시스템 모니터링

**기본 도구**:
```bash
# 디스크 사용량
df -h

# 메모리 사용량
free -h

# 프로세스 상태
systemctl status economy-bot
systemctl status mastodon-web
```

---

### 6.2 로그 관리

**봇 로그**:
```
/home/ubuntu/economy_bot/logs/
├── reward.log          # 재화 지급
├── activity.log        # 활동량 체크
├── command.log         # 명령어 처리
└── error.log           # 에러
```

**로그 로테이션**:
```bash
# /etc/logrotate.d/economy-bot
/home/ubuntu/economy_bot/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
}
```

---

## 7. 개발 환경

### 7.1 로컬 테스트 환경

```bash
# Docker Compose로 로컬 테스트
docker-compose -f docker-compose.dev.yml up

# SQLite DB 로컬 복사
scp ubuntu@server:/path/to/economy.db ./
```

---

### 7.2 배포 프로세스

```bash
# 1. 서버 접속
ssh ubuntu@yourserver.duckdns.org

# 2. 코드 업데이트
cd /home/ubuntu/economy_bot
git pull

# 3. 봇 재시작
sudo systemctl restart economy-bot

# 4. 로그 확인
tail -f logs/error.log
```

---

## 다음 문서

→ [Part 3: 시스템 아키텍처](03-architecture.md)
