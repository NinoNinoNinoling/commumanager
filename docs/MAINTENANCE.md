# 유지보수 시스템 가이드

마녀봇의 자동 유지보수 작업 및 모니터링 시스템입니다.

## 📅 새벽 유지보수 스케줄 (2~6시)

유저 활동이 0인 새벽 시간대를 활용한 자동 유지보수 작업입니다.

### 전체 스케줄

```
02:00 - 데이터베이스 백업
03:00 - 데이터베이스 최적화
04:00 - 재화 정산 + 소셜 분석 + 활동량 체크
05:00 - 로그 정리
05:30 - 시스템 헬스체크
10:00 - 출석 트윗 발행
16:00 - 재화 정산 + 활동량 체크
```

---

## 🔧 유지보수 작업 상세

### 1. DB 백업 (매일 02:00)

**목적:**
- 데이터 손실 방지
- 장애 복구 대비

**작업 내용:**
```python
# bot/tasks.py
@app.task(name='bot.tasks.backup_database_task')
def backup_database_task():
    """데이터베이스 백업 (매일 2시)"""

    # 1. 백업 디렉토리 생성
    backup_dir = 'data/backups'
    os.makedirs(backup_dir, exist_ok=True)

    # 2. 타임스탬프 파일명
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}/economy_backup_{timestamp}.db'

    # 3. SQLite 백업
    shutil.copy2('data/economy.db', backup_file)

    # 4. 압축 (선택)
    with gzip.open(f'{backup_file}.gz', 'wb') as f_out:
        with open(backup_file, 'rb') as f_in:
            shutil.copyfileobj(f_in, f_out)
    os.remove(backup_file)

    # 5. 오래된 백업 삭제 (7일 이상)
    cleanup_old_backups(backup_dir, days=7)

    # 6. 백업 검증
    verify_backup(f'{backup_file}.gz')
```

**보관 정책:**
- 일일 백업: 7일 보관
- 주간 백업: 4주 보관 (매주 일요일)
- 월간 백업: 12개월 보관 (매월 1일)

**복구 방법:**
```bash
# 백업 파일 압축 해제
gunzip data/backups/economy_backup_20250119_020000.db.gz

# 복구
cp data/backups/economy_backup_20250119_020000.db data/economy.db

# 서비스 재시작
./scripts/docker/restart.sh
```

---

### 2. DB 최적화 (매일 03:00)

**목적:**
- 디스크 공간 회수
- 쿼리 성능 향상
- 인덱스 최적화

**작업 내용:**
```python
@app.task(name='bot.tasks.optimize_database_task')
def optimize_database_task():
    """데이터베이스 최적화 (매일 3시)"""

    with get_economy_db() as conn:
        # 1. VACUUM - 삭제된 데이터 공간 회수
        conn.execute('VACUUM')

        # 2. ANALYZE - 통계 정보 갱신
        conn.execute('ANALYZE')

        # 3. 인덱스 재구축 (선택적)
        # conn.execute('REINDEX')

        # 4. 무결성 체크
        integrity_check = conn.execute('PRAGMA integrity_check').fetchone()
        if integrity_check[0] != 'ok':
            logger.error(f'DB 무결성 체크 실패: {integrity_check}')
            # 관리자에게 알림
```

**예상 효과:**
- 디스크 사용량 10~30% 감소
- 쿼리 속도 5~15% 개선

---

### 3. 재화 정산 (매일 04:00, 16:00)

**이미 구현됨** - `bot/reward_bot.py`

**작업 내용:**
- 마지막 정산 이후 답글 수 집계
- 재화 계산 (100개당 10원)
- 트랜잭션 기록
- Redis 캐시 무효화

---

### 4. 소셜 분석 (매일 04:00)

**이미 구현됨** - `bot/activity_checker.py`

**작업 내용:**
- 대화 상대 분석 (48시간)
- 편중 감지 (특정인 30% 초과)
- 고립 감지 (대화 상대 7명 미만)
- 비활동 감지 (7일 중 50% 미만 활동)

---

### 5. 활동량 체크 (매일 04:00, 16:00)

**이미 구현됨** - `bot/activity_checker.py`

**작업 내용:**
- PostgreSQL에서 48시간 답글 수 조회
- 기준 미달 유저 감지 (20개 미만)
- DB에 경고 기록 (자동 발송 안 함)

---

### 6. 로그 정리 (매일 05:00)

**목적:**
- 디스크 공간 확보
- 로그 관리

**작업 내용:**
```python
@app.task(name='bot.tasks.cleanup_logs_task')
def cleanup_logs_task():
    """로그 정리 (매일 5시)"""

    # 1. 오래된 로그 삭제 (30일 이상)
    log_dir = 'logs'
    cutoff_date = datetime.now() - timedelta(days=30)

    for log_file in os.listdir(log_dir):
        file_path = os.path.join(log_dir, log_file)
        if os.path.getmtime(file_path) < cutoff_date.timestamp():
            os.remove(file_path)

    # 2. 로그 압축 (7일 이상)
    compress_old_logs(log_dir, days=7)

    # 3. Redis 메모리 정리
    r = get_redis_client()
    r.flushdb()  # 또는 선택적 삭제

    # 4. Celery 작업 히스토리 정리
    # app.control.purge()
```

**로그 보관 정책:**
- 최근 7일: 원본
- 8~30일: 압축 (.gz)
- 31일 이상: 삭제

---

### 7. 시스템 헬스체크 (매일 05:30)

**목적:**
- 시스템 상태 모니터링
- 문제 조기 발견
- 관리자 알림

**작업 내용:**
```python
@app.task(name='bot.tasks.health_check_task')
def health_check_task():
    """시스템 헬스체크 (매일 5시 30분)"""

    issues = []

    # 1. DB 연결 체크
    try:
        with get_economy_db() as conn:
            conn.execute('SELECT 1').fetchone()
    except Exception as e:
        issues.append(f'SQLite 연결 실패: {e}')

    # 2. PostgreSQL 연결 체크
    try:
        with get_mastodon_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
    except Exception as e:
        issues.append(f'PostgreSQL 연결 실패: {e}')

    # 3. Redis 연결 체크
    try:
        r = get_redis_client()
        r.ping()
    except Exception as e:
        issues.append(f'Redis 연결 실패: {e}')

    # 4. 디스크 공간 체크
    disk_usage = shutil.disk_usage('/')
    free_percent = disk_usage.free / disk_usage.total * 100
    if free_percent < 10:
        issues.append(f'디스크 공간 부족: {free_percent:.1f}% 남음')

    # 5. 마스토돈 API 연결 체크
    try:
        mastodon = create_mastodon_client()
        mastodon.instance()
    except Exception as e:
        issues.append(f'마스토돈 API 연결 실패: {e}')

    # 6. 문제 발견 시 관리자에게 알림
    if issues:
        send_admin_alert(issues)
```

**알림 조건:**
- DB 연결 실패
- Redis 연결 실패
- 디스크 공간 10% 미만
- 마스토돈 API 연결 실패

---

## 📊 모니터링 대시보드 (계획)

### 수집 메트릭
- 시스템 리소스 (CPU, 메모리, 디스크)
- DB 성능 (쿼리 시간, 연결 수)
- 봇 성능 (처리 속도, 에러율)
- 사용자 활동 (일일 활성 유저, 거래 수)

### 알림 규칙
- 에러율 5% 초과
- 응답 시간 1초 초과
- 디스크 공간 10% 미만
- DB 백업 실패

---

## 🔔 관리자 알림 시스템

### 알림 채널
1. **DM** (긴급)
   - DB 연결 실패
   - 백업 실패
   - 디스크 공간 부족

2. **운영진 채널** (중요)
   - 시스템 헬스체크 실패
   - 성능 저하

3. **로그** (참고)
   - 모든 유지보수 작업 결과

### 알림 함수
```python
def send_admin_alert(issues: list):
    """관리자에게 알림 발송"""

    mastodon = create_mastodon_client()
    admin_id = get_setting('admin_account_id')

    message = "🚨 시스템 알림\n\n"
    for issue in issues:
        message += f"• {issue}\n"

    # DM 발송
    mastodon.status_post(
        status=f'@admin {message}',
        visibility='direct'
    )
```

---

## 📈 성능 최적화

### DB 쿼리 최적화
- 인덱스 활용
- N+1 쿼리 제거
- 배치 처리

### Redis 캐싱 전략
- 유저 잔액: 1시간 TTL
- 설정 값: 10분 TTL
- 통계: 5분 TTL

### Celery 튜닝
- Worker 수: CPU 코어 수
- Prefetch: 4
- 타임아웃: 300초

---

## 🛠️ 문제 해결

### DB 백업 실패
```bash
# 로그 확인
./scripts/docker/logs.sh celery-beat

# 수동 백업
docker-compose exec web python -c "from bot.tasks import backup_database_task; backup_database_task()"
```

### DB 최적화 실패
```bash
# 수동 최적화
docker-compose exec web python -c "from bot.tasks import optimize_database_task; optimize_database_task()"
```

### 헬스체크 실패
```bash
# 개별 서비스 체크
docker-compose ps
docker-compose logs web
docker-compose logs redis
```

---

## 📝 체크리스트

### 일일 점검
- [ ] 백업 성공 확인
- [ ] 디스크 공간 확인
- [ ] 에러 로그 확인

### 주간 점검
- [ ] 성능 지표 검토
- [ ] 사용자 피드백 확인
- [ ] 보안 업데이트 확인

### 월간 점검
- [ ] 백업 복구 테스트
- [ ] DB 무결성 체크
- [ ] 의존성 업데이트
