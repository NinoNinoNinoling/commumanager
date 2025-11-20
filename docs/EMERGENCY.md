# 마녀봇 시스템 긴급 대응 매뉴얼

> **대상**: 개발자 부재 시 시스템을 관리해야 하는 기술 담당자
> **목적**: 서버 다운, 오류 등 긴급 상황 대응

---

## ⚠️ 긴급 연락처

**개발자 연락처**: [개발자 연락처]

---

## 📋 목차

1. [서버 상태 확인](#1-서버-상태-확인)
2. [서버 재시작](#2-서버-재시작)
3. [데이터베이스 문제](#3-데이터베이스-문제)
4. [로그 확인 방법](#4-로그-확인-방법)
5. [자주 발생하는 문제](#5-자주-발생하는-문제)
6. [최후의 수단: 완전 초기화](#6-최후의-수단-완전-초기화)

---

## 1. 서버 상태 확인

### 1.1 Flask 서버 실행 여부 확인

```bash
ps aux | grep -E "python.*admin_web|flask"
```

**정상 출력 예시:**
```
root  12345  0.1  2.3  123456  45678  python3 -m admin_web.app
```

**서버가 죽었을 때:**
- 아무 출력 없음 또는 grep 프로세스만 표시

### 1.2 포트 사용 확인

```bash
netstat -tulpn | grep :5000
```

또는

```bash
lsof -i :5000
```

**정상일 때:**
```
tcp  0  0  0.0.0.0:5000  0.0.0.0:*  LISTEN  12345/python3
```

### 1.3 웹 페이지 접속 테스트

```bash
curl http://localhost:5000/api/v1/dashboard/stats
```

**정상일 때:**
- JSON 데이터 반환

**서버 다운일 때:**
```
curl: (7) Failed to connect to localhost port 5000: Connection refused
```

---

## 2. 서버 재시작

### 2.1 한 줄 명령어 (가장 빠름)

```bash
pkill -9 -f "python.*admin_web" && cd /home/user/commumanager && nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

**설명:**
1. 기존 Flask 프로세스 강제 종료
2. 프로젝트 디렉토리로 이동
3. 백그라운드로 Flask 서버 시작
4. 로그를 `flask_server.log`에 저장

### 2.2 단계별 재시작

#### Step 1: 기존 서버 종료

```bash
# 프로세스 ID 확인
ps aux | grep "python.*admin_web"

# PID가 12345라면
kill -9 12345
```

또는 전체 종료:

```bash
pkill -9 -f "python.*admin_web"
```

#### Step 2: 프로젝트 디렉토리 이동

```bash
cd /home/user/commumanager
```

#### Step 3: 서버 시작

**백그라운드 실행 (권장):**
```bash
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

**포그라운드 실행 (테스트용):**
```bash
python3 -m admin_web.app
```

#### Step 4: 서버 시작 확인

```bash
# 3초 대기 후 로그 확인
sleep 3 && tail -30 flask_server.log
```

**정상 시작 시 로그 예시:**
```
==================================================
마녀봇 관리자 웹 서버 시작
==================================================
환경: development
DB: /home/user/commumanager/economy.db
API: /api/v1
아키텍처: Model-Repository-Service-Controller-Route
==================================================
 * Running on http://0.0.0.0:5000
```

**에러 발생 시:**
- 로그에서 에러 메시지 확인
- 아래 "5. 자주 발생하는 문제" 참조

### 2.3 재시작 확인

```bash
# 웹 페이지 접속 테스트
curl http://localhost:5000/api/v1/dashboard/stats

# 또는 브라우저에서
# http://localhost:5000/
```

---

## 3. 데이터베이스 문제

### 3.1 데이터베이스 파일 확인

```bash
ls -lh /home/user/commumanager/economy.db
```

**정상일 때:**
```
-rw-r--r-- 1 root root 2.5M Nov 18 14:30 economy.db
```

**문제:**
- 파일이 없다 → 백업에서 복구 필요
- 크기가 0 → 손상됨, 백업 복구 필요

### 3.2 데이터베이스 락 문제

**증상:**
- 서버가 느려짐
- "database is locked" 에러

**해결:**

```bash
# 데이터베이스 사용 중인 프로세스 확인
lsof /home/user/commumanager/economy.db

# 모든 관련 프로세스 종료
pkill -9 -f "python.*admin_web"
pkill -9 -f "python.*bot"

# WAL 파일 삭제 (주의: 서버 종료 후에만!)
rm -f /home/user/commumanager/economy.db-wal
rm -f /home/user/commumanager/economy.db-shm

# 서버 재시작
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

### 3.3 데이터베이스 백업

**백업 생성:**
```bash
# 날짜 포함 백업 파일명
cp economy.db economy_backup_$(date +%Y%m%d_%H%M%S).db

# 또는 간단히
cp economy.db economy.db.backup
```

**백업 복구:**
```bash
# 1. 서버 종료
pkill -9 -f "python.*admin_web"

# 2. 현재 DB 백업 (만약을 위해)
mv economy.db economy_broken.db

# 3. 백업 파일 복구
cp economy_backup_YYYYMMDD_HHMMSS.db economy.db

# 4. 서버 시작
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

### 3.4 데이터베이스 무결성 검사

```bash
# SQLite 직접 접근
python3 -c "
import sqlite3
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()
cursor.execute('PRAGMA integrity_check')
result = cursor.fetchone()
print('DB 상태:', result[0])
conn.close()
"
```

**정상:**
```
DB 상태: ok
```

**문제 발생:**
```
DB 상태: *** in database main ***
```
→ 백업에서 복구 필요

---

## 4. 로그 확인 방법

### 4.1 Flask 서버 로그

**로그 파일 위치:**
```
/home/user/commumanager/flask_server.log
```

**실시간 로그 보기:**
```bash
tail -f flask_server.log
```

**최근 100줄 보기:**
```bash
tail -100 flask_server.log
```

**에러만 필터링:**
```bash
grep -i error flask_server.log | tail -50
```

### 4.2 시스템 로그

```bash
# 시스템 전체 로그 (Ubuntu/Debian)
journalctl -xe

# Python 관련 로그만
journalctl | grep python

# 최근 1시간 로그
journalctl --since "1 hour ago"
```

### 4.3 디스크 사용량 확인

```bash
# 전체 디스크 사용량
df -h

# 프로젝트 디렉토리 크기
du -sh /home/user/commumanager
```

**로그 파일이 너무 클 때:**
```bash
# 로그 파일 크기 확인
ls -lh flask_server.log

# 로그 파일 초기화 (주의: 기존 로그 삭제됨)
> flask_server.log

# 또는 백업 후 초기화
mv flask_server.log flask_server.log.old
touch flask_server.log
```

---

## 5. 자주 발생하는 문제

### 문제 1: ModuleNotFoundError: No module named 'flask'

**증상:**
```
ModuleNotFoundError: No module named 'flask'
```

**원인:** Python 패키지 미설치

**해결:**
```bash
pip3 install --break-system-packages flask requests python-dotenv psycopg2-binary
```

### 문제 2: 데이터베이스 파일 없음

**증상:**
```
⚠️  데이터베이스가 없습니다: /home/user/commumanager/economy.db
```

**해결:**
```bash
# 백업 파일 확인
ls -lh economy*.db

# 백업이 있다면 복구
cp economy_backup_YYYYMMDD.db economy.db

# 백업이 없다면 초기화 (주의: 모든 데이터 손실!)
python3 init_db.py economy.db
```

### 문제 3: 포트 5000이 이미 사용 중

**증상:**
```
OSError: [Errno 98] Address already in use
```

**해결:**
```bash
# 포트 5000 사용 프로세스 확인
lsof -i :5000

# PID 확인 후 종료 (예: PID가 12345)
kill -9 12345

# 또는 전체 Flask 프로세스 종료
pkill -9 -f "python.*admin_web"
```

### 문제 4: Permission Denied (권한 오류)

**증상:**
```
PermissionError: [Errno 13] Permission denied: 'economy.db'
```

**해결:**
```bash
# 파일 소유자 및 권한 확인
ls -l economy.db

# 권한 수정
chmod 666 economy.db

# 또는 소유자 변경 (현재 사용자로)
chown $USER:$USER economy.db
```

### 문제 5: 500 Internal Server Error

**증상:** 웹 페이지에서 500 에러

**해결:**

1. **로그 확인:**
```bash
tail -50 flask_server.log
```

2. **일반적인 원인:**
   - 데이터베이스 락
   - 데이터베이스 손상
   - 코드 오류

3. **디버그 모드 활성화:**
```bash
# 환경 변수 설정 후 재시작
export FLASK_ENV=development
python3 -m admin_web.app
```

4. **에러 메시지에서 원인 파악 후 조치**

### 문제 6: 웹 페이지는 뜨는데 통계가 0

**원인:** 데이터베이스에 데이터 없음

**해결:**
```bash
# 테스트 데이터 생성
python3 scripts/seed_test_data.py

# 데이터베이스 테이블 개수 확인
python3 -c "
import sqlite3
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
print('사용자 수:', cursor.fetchone()[0])
conn.close()
"
```

---

## 6. 최후의 수단: 완전 초기화

### ⚠️ 경고

**이 작업은 모든 데이터를 삭제합니다!**
- 사용자 정보
- 거래 내역
- 경고 기록
- 휴식 신청
- 이벤트
- 아이템
- 관리자 로그

**백업을 먼저 만드세요!**

### 6.1 백업 생성

```bash
cd /home/user/commumanager

# 전체 백업
tar -czf commumanager_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  economy.db \
  flask_server.log

# 백업 확인
ls -lh commumanager_backup_*.tar.gz
```

### 6.2 완전 초기화 절차

```bash
# 1. 모든 서버 프로세스 종료
pkill -9 -f "python.*admin_web"
pkill -9 -f "python.*bot"

# 2. 데이터베이스 삭제
rm -f economy.db economy.db-wal economy.db-shm

# 3. 데이터베이스 재생성
python3 init_db.py economy.db

# 4. 테스트 데이터 생성 (선택)
python3 scripts/seed_test_data.py

# 5. 서버 시작
nohup python3 -m admin_web.app > flask_server.log 2>&1 &

# 6. 확인
sleep 3
curl http://localhost:5000/api/v1/dashboard/stats
```

---

## 📞 도움 요청

### 위 방법으로 해결이 안 될 때

1. **로그 파일 수집:**
```bash
# 로그 파일 복사
cp flask_server.log ~/flask_error_$(date +%Y%m%d_%H%M%S).log
```

2. **상황 메모:**
   - 무엇을 했을 때 문제가 발생했는지
   - 에러 메시지 전문
   - 시도한 해결 방법

3. **개발자에게 연락:**
   - 로그 파일 전송
   - 상황 설명

---

## 🔧 유용한 명령어 모음

### 빠른 참조

```bash
# 서버 상태 확인
ps aux | grep "python.*admin_web"

# 서버 재시작 (한 줄)
pkill -9 -f "python.*admin_web" && cd /home/user/commumanager && nohup python3 -m admin_web.app > flask_server.log 2>&1 &

# 로그 실시간 보기
tail -f flask_server.log

# 로그 에러만 보기
grep -i error flask_server.log | tail -30

# DB 백업
cp economy.db economy_backup_$(date +%Y%m%d).db

# 테스트 데이터 생성
python3 scripts/seed_test_data.py

# 웹 페이지 테스트
curl http://localhost:5000/api/v1/dashboard/stats

# 디스크 사용량
df -h

# 포트 사용 확인
lsof -i :5000
```

---

## 📝 체크리스트

서버가 다운되었을 때:

- [ ] 서버 프로세스가 실행 중인가?
- [ ] 포트 5000이 사용 중인가?
- [ ] 데이터베이스 파일이 존재하는가?
- [ ] 로그 파일에 에러가 있는가?
- [ ] 디스크 공간이 충분한가?
- [ ] 백업 파일이 있는가?

---

**마지막 업데이트**: 2025-11-18
**문서 버전**: 1.0
