# 성능 분석 및 최적화 방안

## Oracle 프리티어 스펙

### 하드웨어
- **CPU**: Ampere A1 4 OCPU (ARM64)
- **RAM**: 24GB
- **Storage**: 100GB (확장 가능)
- **Network**: 무제한

### 예상 리소스 사용량

#### 마스토돈 (휘핑 에디션)
```
- PostgreSQL: ~2GB RAM
- Redis: ~500MB RAM
- Web (Puma): ~1GB RAM
- Streaming: ~500MB RAM
- Sidekiq: ~500MB RAM
------------------------------
합계: ~4.5GB RAM, 1~2 OCPU
```

#### 관리 봇 시스템
```
- 재화 지급 봇 (24/7 Streaming): ~200MB RAM, 0.2 OCPU
- 활동량 체크 봇 (하루 2회 실행): ~100MB RAM (실행 시)
- 명령어 처리 봇 (Streaming): ~200MB RAM, 0.2 OCPU
- 관리자 봇 (공지 발송): ~100MB RAM (실행 시)
------------------------------
합계: ~600MB RAM, 0.5 OCPU (상시)
```

#### Flask 관리자 웹
```
- Gunicorn (2 workers): ~400MB RAM, 0.3 OCPU
- Nginx: ~50MB RAM
------------------------------
합계: ~450MB RAM, 0.3 OCPU
```

### 총 예상 사용량

```
마스토돈:     4.5GB RAM, 1.5 OCPU
봇 시스템:    0.6GB RAM, 0.5 OCPU
관리자 웹:    0.5GB RAM, 0.3 OCPU
시스템:       1.0GB RAM, 0.5 OCPU
--------------------------------
총합:         6.6GB RAM, 2.8 OCPU
여유:        17.4GB RAM, 1.2 OCPU
```

**결론**: Oracle 프리티어로 충분히 운영 가능

## 성능 최적화 전략

### 1. 마스토돈 최적화

#### PostgreSQL
```sql
-- 연결 수 제한
max_connections = 50

-- 메모리 설정
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 16MB
```

#### Redis
```
maxmemory 512mb
maxmemory-policy allkeys-lru
```

#### Puma (Web Server)
```ruby
# config/puma.rb
workers 2
threads 2, 4
```

### 2. 봇 최적화

#### Streaming API 연결 최소화
```python
# 재화 지급 봇 + 명령어 처리 봇 통합
# 하나의 Streaming 연결로 모든 이벤트 처리
class UnifiedBot:
    def __init__(self):
        self.reward_handler = RewardHandler()
        self.command_handler = CommandHandler()

    def on_notification(self, notification):
        # 답글 → 재화 지급
        if notification['type'] == 'mention':
            self.reward_handler.process(notification)
            self.command_handler.process(notification)
```

#### 활동량 체크 벌크 처리
```python
# PostgreSQL 읽기 전용 연결 (Read Replica 효과)
# 하루 2회만 실행 (4시, 16시)
def check_activity():
    # 한 번의 쿼리로 모든 유저 처리
    query = """
        SELECT account_id, COUNT(*) as reply_count
        FROM statuses
        WHERE created_at > NOW() - INTERVAL '48 hours'
        AND in_reply_to_id IS NOT NULL
        GROUP BY account_id
    """
```

#### SQLite 최적화
```python
# WAL 모드 (동시 읽기/쓰기)
conn.execute("PRAGMA journal_mode = WAL")
conn.execute("PRAGMA synchronous = NORMAL")
conn.execute("PRAGMA cache_size = -64000")  # 64MB
```

### 3. 관리자 웹 최적화

#### Gunicorn 설정
```python
# gunicorn.conf.py
workers = 2  # CPU 코어 수에 따라 조정
worker_class = 'sync'
timeout = 30
keepalive = 2
```

#### 정적 파일 캐싱
```nginx
# Nginx 설정
location /static {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

#### DB 쿼리 최적화
```python
# 페이지네이션 + 인덱스 활용
# N+1 쿼리 방지
```

### 4. 모니터링

#### 리소스 모니터링 스크립트
```bash
#!/bin/bash
# monitor.sh

echo "=== CPU Usage ==="
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'

echo "=== Memory Usage ==="
free -h | grep Mem | awk '{print $3 "/" $2}'

echo "=== Disk Usage ==="
df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}'

echo "=== Docker Containers ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

#### systemd 서비스 모니터링
```bash
# 봇 상태 확인
systemctl status reward-bot
systemctl status activity-checker
```

## 예상 성능 (50명 커뮤니티 기준)

### 일반 사용 시나리오

#### 답글 활동
- 하루 평균 답글: 50명 × 30개 = 1,500개
- 재화 지급 트랜잭션: 1,500건/일
- DB Insert: 1,500 × 2 (transactions, users update) = 3,000 쿼리/일
- **평균 부하**: 무시 가능 (초당 0.035 쿼리)

#### 활동량 체크
- 하루 2회 실행 (4시, 16시)
- PostgreSQL 읽기 쿼리: 1개 (벌크)
- 경고 대상: 최대 10명
- SQLite 쓰기: 10건
- **실행 시간**: 5초 이내

#### 관리자 웹
- 동시 접속: 최대 3~5명
- 페이지 로딩: 0.5초 이내
- **부하**: 매우 낮음

### 피크 시나리오

#### 이벤트 발생 시
- 동시 답글: 100개/분
- Streaming API 지연: 1~2초
- 재화 지급: 실시간 처리
- **체감 지연**: 없음

#### 활동량 체크 시간 (4시, 16시)
- PostgreSQL 쿼리: 2~3초
- 경고 발송: 5초 이내
- **시스템 영향**: 미미

## 병목 지점 및 대응

### 1. PostgreSQL 부하
**원인**: 마스토돈 자체 트래픽
**대응**:
- 읽기 전용 쿼리만 사용 (봇)
- 하루 2회만 실행 (활동량 체크)
- 인덱스 최적화

### 2. SQLite 동시 쓰기
**원인**: 여러 봇이 동시에 쓰기
**대응**:
- WAL 모드 활성화
- 쓰기 재시도 로직
- 큐 시스템 (선택)

### 3. Streaming API 연결 수
**원인**: 봇마다 별도 연결
**대응**:
- 통합 봇 (하나의 Streaming 연결)
- 이벤트 핸들러 분리

### 4. 메모리 누수
**원인**: 장시간 실행
**대응**:
- systemd 자동 재시작
- 메모리 사용량 모니터링
- 로그 로테이션

## 권장 사항

### 필수
1. ✅ WAL 모드 활성화 (SQLite)
2. ✅ 통합 봇 구조 (하나의 Streaming 연결)
3. ✅ 벌크 쿼리 (활동량 체크)
4. ✅ 인덱스 최적화
5. ✅ systemd 자동 재시작

### 선택
1. Redis 캐싱 (조회 성능 향상)
2. 큐 시스템 (Celery + Redis)
3. CDN (정적 파일)
4. 로그 분석 도구

## 결론

**Oracle 프리티어 (4 OCPU, 24GB)는 50명 규모 커뮤니티에 충분합니다.**

- 예상 사용량: 6.6GB RAM, 2.8 OCPU
- 여유: 17.4GB RAM, 1.2 OCPU
- 100명까지 확장 가능
- 추가 비용 없음

**주의사항**:
- 마스토돈 자체가 주요 리소스 소비
- 봇은 최소한의 리소스만 사용
- 적절한 최적화로 안정적 운영 가능
