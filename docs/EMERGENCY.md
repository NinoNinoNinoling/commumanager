# 🚨 긴급 상황 대응 매뉴얼

> **대상**: 개발자 부재 시 긴급 대응이 필요한 관리자
> **목적**: 시스템 장애 발생 시 신속한 복구

---

## ⚠️ 이 문서를 언제 사용하나요?

- ❌ 서버가 다운되어 접속이 안 될 때
- ❌ API 요청이 응답하지 않을 때
- ❌ 웹 페이지가 에러를 표시할 때
- ❌ 데이터베이스 오류가 발생할 때
- ❌ 봇이 작동하지 않을 때

---

## 📋 목차

1. [긴급 연락처](#긴급-연락처)
2. [서버 상태 확인](#서버-상태-확인)
3. [서버 재시작](#서버-재시작)
4. [데이터베이스 문제](#데이터베이스-문제)
5. [API 응답 없음](#api-응답-없음)
6. [웹 페이지 에러](#웹-페이지-에러)
7. [로그 확인 방법](#로그-확인-방법)
8. [데이터 백업/복구](#데이터-백업복구)
9. [자주 발생하는 문제](#자주-발생하는-문제)
10. [최후의 수단](#최후의-수단)

---

## 긴급 연락처

### 1순위: 개발자
- **이름**: [개발자 이름]
- **연락처**: [전화번호]
- **이메일**: [이메일]
- **카카오톡**: [ID]

### 2순위: 시스템 관리자
- **이름**: [관리자 이름]
- **연락처**: [전화번호]

### 3순위: 백업 담당자
- **이름**: [백업 담당자]
- **연락처**: [전화번호]

---

## 서버 상태 확인

### 단계 1: 서버 접속 확인

SSH로 서버에 접속할 수 있는지 확인:

```bash
ssh 사용자명@서버주소
```

**접속이 안 되면**:
- 서버 호스팅 업체에 문의 (GCP, AWS 등)
- 네트워크 문제일 가능성

**접속이 되면**:
- 다음 단계로 진행

---

### 단계 2: Flask 서버 실행 확인

서버에 접속한 후:

```bash
# Flask 프로세스 확인
ps aux | grep flask
ps aux | grep python

# 실행 중이면 다음과 같이 표시됨:
# user  12345  0.5  2.0  123456  45678 ?  S  10:00  0:05 python3 -m admin_web.app
```

**결과 해석**:
- ✅ 프로세스가 보이면: Flask 서버가 실행 중
- ❌ 프로세스가 안 보이면: Flask 서버가 중지됨 → [서버 재시작](#서버-재시작)으로 이동

---

### 단계 3: 포트 열림 확인

```bash
# 5000번 포트 확인
netstat -tuln | grep 5000

# 또는
lsof -i :5000
```

**결과 해석**:
- ✅ 포트가 LISTEN 상태면: 정상
- ❌ 아무것도 안 나오면: Flask 서버가 안 띄워짐 → [서버 재시작](#서버-재시작)

---

## 서버 재시작

### 🔴 주의사항

**재시작 전 반드시 확인**:
1. 현재 접속 중인 유저가 있는지 확인
2. 예정된 작업이 없는지 확인
3. 가능하면 공지 후 재시작

---

### 단계 1: 기존 프로세스 종료

```bash
# Flask 프로세스 찾기
ps aux | grep flask

# 프로세스 ID(PID) 확인 후 종료
kill -9 [PID]

# 예시:
# ps aux | grep flask
# user  12345 ...
# kill -9 12345
```

**모든 Flask 프로세스 강제 종료** (주의!):
```bash
pkill -9 -f "python.*admin_web"
```

---

### 단계 2: 프로젝트 디렉토리 이동

```bash
cd /home/user/commumanager
```

---

### 단계 3: 데이터베이스 확인

```bash
# economy.db 파일 존재 확인
ls -lh economy.db

# 파일이 없으면:
python3 init_db.py economy.db
```

---

### 단계 4: Flask 서버 시작

**개발 모드** (디버깅용):
```bash
FLASK_ENV=development DATABASE_PATH=economy.db python3 -m admin_web.app
```

**프로덕션 모드** (백그라운드 실행):
```bash
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

**서버 시작 확인**:
```bash
# 로그 확인
tail -f flask_server.log

# 다음과 같이 표시되면 정상:
# ============================================================
# 마녀봇 관리자 웹 서버 시작
# ============================================================
# 환경: development
# DB: economy.db
# API: /api/v1
# ============================================================
```

---

### 단계 5: 서버 접속 테스트

**웹 브라우저로 확인**:
```
http://서버주소:5000/dashboard
```

**curl로 확인**:
```bash
curl http://localhost:5000/api/v1/dashboard/stats
```

**정상 응답 예시**:
```json
{
  "users": {
    "total": 10,
    "active_24h": 5,
    "on_vacation": 1
  },
  ...
}
```

---

## 데이터베이스 문제

### 증상

- "unable to open database file" 에러
- "database is locked" 에러
- API 요청 시 500 에러

---

### 해결 방법 1: 데이터베이스 파일 권한 확인

```bash
# 권한 확인
ls -l economy.db

# 권한 수정 (읽기/쓰기 권한 부여)
chmod 664 economy.db

# 소유자 확인 및 변경
chown 사용자명:그룹명 economy.db
```

---

### 해결 방법 2: 데이터베이스 잠금 해제

```bash
# SQLite 프로세스 확인
lsof | grep economy.db

# 잠금 프로세스 종료
kill -9 [PID]

# Flask 서버 재시작
pkill -9 -f "python.*admin_web"
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

---

### 해결 방법 3: 데이터베이스 복구

**백업에서 복구**:
```bash
# 백업 파일 확인
ls -lh backups/

# 최신 백업 복사
cp backups/economy_backup_YYYYMMDD.db economy.db

# Flask 서버 재시작
```

**백업이 없으면**:
```bash
# 새 데이터베이스 생성 (주의: 기존 데이터 삭제!)
mv economy.db economy_broken.db
python3 init_db.py economy.db
```

---

## API 응답 없음

### 증상

- Postman에서 요청 시 타임아웃
- 웹 페이지가 무한 로딩
- curl 명령어 응답 없음

---

### 단계 1: Flask 서버 로그 확인

```bash
tail -n 100 flask_server.log
```

**에러 메시지 찾기**:
- `Error:` 또는 `Exception:`으로 시작하는 줄
- `Traceback:` 으로 시작하는 줄

**일반적인 에러**:
- `sqlite3.OperationalError`: 데이터베이스 문제
- `ModuleNotFoundError`: 패키지 설치 필요
- `port already in use`: 포트 충돌

---

### 단계 2: 의존성 패키지 확인

```bash
# 가상환경 활성화 (있는 경우)
source venv/bin/activate

# 패키지 재설치
pip install -r requirements.txt
```

---

### 단계 3: 포트 충돌 해결

```bash
# 5000번 포트 사용 중인 프로세스 확인
lsof -i :5000

# 프로세스 종료
kill -9 [PID]

# Flask 서버 재시작
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

---

## 웹 페이지 에러

### 증상: 500 Internal Server Error

**원인**: 서버 내부 오류

**해결**:
1. Flask 서버 로그 확인:
   ```bash
   tail -n 50 flask_server.log
   ```

2. 에러 메시지 확인 후 [자주 발생하는 문제](#자주-발생하는-문제) 참조

3. 해결 안 되면 서버 재시작

---

### 증상: 404 Not Found

**원인**: 잘못된 URL 또는 라우트 문제

**해결**:
1. URL 확인:
   - ✅ 올바른 예: `http://서버주소:5000/dashboard`
   - ❌ 잘못된 예: `http://서버주소:5000/dash`

2. API 엔드포인트 확인:
   - `docs/postman_collection.json` 참조

---

### 증상: 빈 페이지 또는 템플릿 에러

**원인**: 템플릿 파일 누락 또는 데이터 문제

**해결**:
1. 템플릿 파일 확인:
   ```bash
   ls admin_web/templates/
   # base.html, dashboard.html, logs.html 존재해야 함
   ```

2. 데이터 확인:
   ```bash
   # API가 정상 응답하는지 확인
   curl http://localhost:5000/api/v1/dashboard/stats
   ```

---

## 로그 확인 방법

### Flask 서버 로그

```bash
# 실시간 로그 보기
tail -f flask_server.log

# 최근 100줄 보기
tail -n 100 flask_server.log

# 에러만 필터링
grep -i "error" flask_server.log
grep -i "exception" flask_server.log
```

---

### 시스템 로그

```bash
# 시스템 로그 확인
sudo journalctl -u flask-admin-web -n 100

# 또는
sudo tail -n 100 /var/log/syslog | grep flask
```

---

### 관리자 활동 로그

**웹 페이지에서**:
```
http://서버주소:5000/logs
```

**API로**:
```bash
curl http://localhost:5000/api/v1/admin-logs?limit=100
```

---

## 데이터 백업/복구

### 수동 백업

```bash
# 백업 디렉토리 생성
mkdir -p backups

# 데이터베이스 백업
cp economy.db backups/economy_backup_$(date +%Y%m%d_%H%M%S).db

# 백업 확인
ls -lh backups/
```

---

### 자동 백업 설정 (cron)

```bash
# cron 편집
crontab -e

# 매일 새벽 3시 자동 백업 추가
0 3 * * * cd /home/user/commumanager && cp economy.db backups/economy_backup_$(date +\%Y\%m\%d).db

# 저장 후 종료 (:wq)
```

---

### 복구

```bash
# 백업 목록 확인
ls -lh backups/

# 복구할 백업 선택
cp backups/economy_backup_YYYYMMDD_HHMMSS.db economy.db

# Flask 서버 재시작
pkill -9 -f "python.*admin_web"
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

---

## 자주 발생하는 문제

### 문제 1: "No module named 'admin_web'"

**원인**: Python 경로 문제

**해결**:
```bash
# 프로젝트 루트 디렉토리에서 실행
cd /home/user/commumanager

# PYTHONPATH 설정
export PYTHONPATH=/home/user/commumanager:$PYTHONPATH

# Flask 서버 시작
python3 -m admin_web.app
```

---

### 문제 2: "Address already in use"

**원인**: 5000번 포트가 이미 사용 중

**해결**:
```bash
# 포트 사용 프로세스 확인
lsof -i :5000

# 프로세스 종료
kill -9 [PID]

# Flask 서버 재시작
```

---

### 문제 3: "database is locked"

**원인**: 다른 프로세스가 데이터베이스를 사용 중

**해결**:
```bash
# 모든 Flask 프로세스 종료
pkill -9 -f "python.*admin_web"

# 잠시 대기 (5초)
sleep 5

# Flask 서버 재시작
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

---

### 문제 4: API 응답이 너무 느림

**원인**: 데이터베이스 크기 또는 쿼리 성능

**해결**:
```bash
# 데이터베이스 크기 확인
ls -lh economy.db

# 10MB 이상이면 최적화 필요
sqlite3 economy.db "VACUUM;"

# Flask 서버 재시작
```

---

### 문제 5: 웹 페이지에 데이터가 안 보임

**원인**: 데이터베이스가 비어있음

**해결**:
```bash
# 테스트 데이터 생성
python3 scripts/seed_test_data.py

# 웹 페이지 새로고침
```

---

## 최후의 수단

### 상황: 위의 모든 방법으로도 해결 안 됨

**단계별 조치**:

---

### 1. 현재 상태 저장

```bash
# 로그 백업
cp flask_server.log flask_server_error_$(date +%Y%m%d_%H%M%S).log

# 데이터베이스 백업
cp economy.db economy_error_$(date +%Y%m%d_%H%M%S).db

# 설정 파일 백업
cp -r admin_web admin_web_backup_$(date +%Y%m%d_%H%M%S)
```

---

### 2. 시스템 완전 초기화

```bash
# 프로젝트 디렉토리로 이동
cd /home/user/commumanager

# 모든 Flask 프로세스 종료
pkill -9 -f "python.*admin_web"

# 가상환경 재생성 (있는 경우)
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 패키지 재설치
pip install --upgrade pip
pip install -r requirements.txt

# 데이터베이스 재생성
mv economy.db economy_old.db
python3 init_db.py economy.db

# Flask 서버 시작
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

---

### 3. 코드 재배포

```bash
# Git에서 최신 코드 받기
git pull origin claude/api-testing-server-work-018RNKmZgKp1VXDS8RHJ5w9u

# 패키지 재설치
pip install -r requirements.txt

# 데이터베이스 초기화
python3 init_db.py economy.db

# Flask 서버 시작
nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

---

### 4. 개발자에게 연락

**연락 시 제공할 정보**:

1. **에러 로그**:
   ```bash
   tail -n 200 flask_server.log > error_report.txt
   ```

2. **시스템 정보**:
   ```bash
   echo "=== Python 버전 ===" >> error_report.txt
   python3 --version >> error_report.txt

   echo "=== 설치된 패키지 ===" >> error_report.txt
   pip list >> error_report.txt

   echo "=== 데이터베이스 정보 ===" >> error_report.txt
   ls -lh economy.db >> error_report.txt
   ```

3. **발생한 문제 설명**:
   - 언제 문제가 발생했는지
   - 어떤 작업을 하던 중이었는지
   - 에러 메시지가 있었는지

**error_report.txt 파일을 개발자에게 전달**

---

## 🆘 긴급 연락 절차

1. **즉시 연락**: 개발자에게 전화 또는 문자
2. **상황 공지**: 커뮤니티에 시스템 점검 공지
3. **로그 수집**: `error_report.txt` 생성
4. **대기**: 개발자의 지시 대기

---

## ✅ 복구 후 확인 사항

서버 재시작 후 반드시 확인:

1. **웹 페이지 접속**:
   - [ ] http://서버주소:5000/dashboard
   - [ ] http://서버주소:5000/logs

2. **API 테스트**:
   ```bash
   curl http://localhost:5000/api/v1/dashboard/stats
   ```

3. **데이터 확인**:
   - [ ] 유저 목록 조회
   - [ ] 경고 목록 조회
   - [ ] 관리자 로그 조회

4. **기능 테스트**:
   - [ ] 유저 검색
   - [ ] 재화 조정
   - [ ] 경고 발송

---

## 📞 추가 리소스

- **일반 관리자 가이드**: `docs/ADMIN_GUIDE.md`
- **API 문서**: `docs/postman_collection.json`
- **Postman Collection 사용법**: Postman 설치 후 Import

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-01-18
**작성자**: [개발자 이름]

---

## 🔖 빠른 참조

### 서버 재시작 (한 줄 명령어)

```bash
pkill -9 -f "python.*admin_web" && cd /home/user/commumanager && nohup python3 -m admin_web.app > flask_server.log 2>&1 &
```

### 로그 확인

```bash
tail -f flask_server.log
```

### 데이터베이스 백업

```bash
cp economy.db backups/economy_backup_$(date +%Y%m%d_%H%M%S).db
```

### API 테스트

```bash
curl http://localhost:5000/api/v1/dashboard/stats
```
