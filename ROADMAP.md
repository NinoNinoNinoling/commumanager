# 마녀봇 관리 시스템 로드맵

> 마스토돈 커뮤니티 관리 시스템 개발 진행 상황 및 계획

---

## 🎯 당장 할일 (2시간 테스트 플랜)

### 1단계: 환경 준비 (10분)
- [ ] 프로젝트 디렉토리로 이동
- [ ] Python 가상환경 생성 및 활성화
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # Linux/Mac
  ```
- [ ] 의존성 설치: `pip install -r requirements.txt`
- [ ] `.env` 파일 생성 (`.env.example` 복사)
- [ ] `.env` 편집 - 최소한 `SECRET_KEY`, `MASTODON_*` 설정

### 2단계: 데이터베이스 초기화 (5분)
- [ ] DB 생성: `python init_db.py`
- [ ] 테스트 데이터 삽입: `python scripts/seed_test_data.py`
- [ ] DB 확인:
  ```bash
  sqlite3 economy.db "SELECT COUNT(*) FROM users;"
  sqlite3 economy.db "SELECT COUNT(*) FROM transactions;"
  ```

### 3단계: Admin Web 서버 실행 (5분)
- [ ] Flask 서버 시작: `cd admin_web && python app.py`
- [ ] 브라우저 접속: `http://localhost:5000`
- [ ] 로그인 페이지 확인
- [ ] 에러 로그 확인

### 4단계: API 자동 테스트 (20분)
- [ ] API 테스트 실행: `python scripts/test_all_api.py`
- [ ] 성공/실패 결과 확인
- [ ] 실패한 API 목록 기록

### 5단계: 수동 웹 테스트 (40분)
**OAuth 우회 (테스트용)** - `admin_web/app.py`에 임시 라우트 추가:
```python
@app.route('/debug-login')
def debug_login():
    session['user_id'] = 'test_admin'
    session['username'] = 'TestAdmin'
    return redirect('/dashboard')
```

**체크리스트:**
- [ ] `/debug-login` 접속 → 대시보드 이동 확인
- [ ] 대시보드 - 통계 표시 확인
- [ ] 사용자 목록 - 테스트 사용자 표시 확인
- [ ] 사용자 상세 - 거래 내역 확인
- [ ] 경고 목록 - 경고 생성/삭제 테스트
- [ ] 휴가 목록 - 휴가 신청/승인 테스트
- [ ] 이벤트 관리 - 이벤트 생성/수정/삭제 테스트
- [ ] 상점 - 아이템 생성/수정 테스트
- [ ] 설정 - 설정값 변경 테스트
- [ ] 로그 - 관리자 로그 기록 확인

### 6단계: 문제 기록 (30분)
- [ ] 발견한 에러 문서화
- [ ] 성능 문제 기록
- [ ] UI/UX 개선사항 메모

### 7단계: 버그 수정 (시간 남으면)
- [ ] 심각한 버그 1-2개 수정
- [ ] 수정 사항 커밋

---

## ✅ Phase 1: 기본 아키텍처 설계 (완료)

- [x] 프로젝트 구조 설계 (5-layer architecture)
- [x] Model-Repository-Service-Controller-Route 패턴 구현
- [x] 데이터베이스 모델 정의 (11개 모델)
- [x] Flask 애플리케이션 기본 구조
- [x] 환경 설정 시스템 (.env)

---

## ✅ Phase 2: 인증 시스템 (완료)

- [x] Mastodon OAuth 2.0 인증 구현
- [x] Flask 세션 관리
- [x] 로그인/로그아웃 라우트
- [x] `@login_required` 데코레이터
- [x] 관리자 권한 검증

---

## ✅ Phase 3: 데이터 레이어 구현 (완료)

### Repository Layer
- [x] UserRepository (8개 메서드)
- [x] WarningRepository (5개 메서드)
- [x] VacationRepository (7개 메서드)
- [x] TransactionRepository (5개 메서드)
- [x] EventRepository (6개 메서드)
- [x] ItemRepository (6개 메서드)
- [x] SettingRepository (4개 메서드)
- [x] AdminLogRepository (5개 메서드)
- [x] 모든 레포지토리 메서드 구현 완료 (100% 커버리지)

### Database Context
- [x] SQLite 데이터베이스 컨텍스트 매니저
- [x] `get_economy_db()` 구현
- [x] Row factory 설정

---

## ✅ Phase 4: 비즈니스 로직 레이어 (완료)

### Service Layer
- [x] UserService (사용자 관리, 통계, 거래 내역)
- [x] DashboardService (대시보드 통계 집계)
- [x] WarningService (경고 관리)
- [x] VacationService (휴가 관리)
- [x] EventService (이벤트 관리)
- [x] ItemService (상점 아이템 관리)
- [x] SettingService (설정 관리)
- [x] AdminLogService (관리자 로그)
- [x] 모든 TODO 주석 제거 및 실제 구현 완료

---

## ✅ Phase 5: API 엔드포인트 (완료)

### REST API
- [x] `/api/users` - 사용자 목록/상세/생성/수정/삭제
- [x] `/api/warnings` - 경고 목록/생성/삭제
- [x] `/api/vacations` - 휴가 목록/생성/삭제
- [x] `/api/events` - 이벤트 목록/생성/수정/삭제
- [x] `/api/items` - 상점 아이템 목록/생성/수정/삭제
- [x] `/api/settings` - 설정 조회/수정
- [x] `/api/logs` - 관리자 로그 조회
- [x] 모든 라우트 파라미터 수정 완료

---

## ✅ Phase 6: 웹 인터페이스 (완료)

### HTML Templates
- [x] `base.html` - 기본 레이아웃 (Bootstrap 5)
- [x] `login.html` - 로그인 페이지
- [x] `dashboard.html` - 대시보드
- [x] `user_list.html` - 사용자 목록
- [x] `user_detail.html` - 사용자 상세
- [x] `warning_list.html` - 경고 목록
- [x] `vacation_list.html` - 휴가 목록
- [x] `event_list.html` - 이벤트 목록
- [x] `item_list.html` - 상점 아이템 목록
- [x] `settings.html` - 설정 페이지
- [x] `logs.html` - 관리자 로그
- [x] `error.html` - 에러 페이지

### Web Routes
- [x] 모든 웹 라우트 구현
- [x] 서비스 메서드 호출 수정 완료
- [x] 에러 핸들링 추가

---

## ✅ Phase 7: 문서화 (완료)

- [x] README.md (프로젝트 소개, 설치 방법)
- [x] ADMIN_GUIDE.md (관리자 사용 가이드)
- [x] SCREEN_EXAMPLES.md (화면 목업)
- [x] API_REFERENCE.md (API 문서)
- [x] SVG 목업 이미지 6개 생성
  - [x] login.svg - 로그인 화면
  - [x] dashboard.svg - 대시보드
  - [x] logs.svg - 로그 뷰어
  - [x] users.svg - 사용자 목록
  - [x] events.svg - 이벤트 관리
  - [x] shop.svg - 상점 관리
- [x] 코드 주석 및 docstring 작성

---

## ✅ Phase 8: 데이터베이스 & 테스트 도구 (완료)

### Database Setup
- [x] `init_db.py` - 데이터베이스 초기화 스크립트 (377줄)
  - [x] 11개 테이블 생성 (users, transactions, warnings, etc.)
  - [x] 인덱스 설정
  - [x] 외래키 제약조건
  - [x] 초기 설정 데이터 삽입

### Testing Scripts
- [x] `scripts/test_all_api.py` - 자동 API 테스트 스크립트 (601줄)
  - [x] 모든 REST API 엔드포인트 자동 테스트
  - [x] 색상 코드 출력으로 결과 확인
  - [x] 상세한 테스트 리포트 생성
- [x] `scripts/seed_test_data.py` - 테스트 데이터 생성 스크립트 (534줄)
  - [x] 샘플 사용자 생성
  - [x] 거래/경고/휴가/이벤트/아이템 데이터 생성
  - [x] 실제 운영 시뮬레이션 데이터

### Manual Tests (진행 예정)
- [ ] 웹 인터페이스 E2E 테스트
- [ ] 실제 마스토돈 서버 연동 테스트
- [ ] 브라우저 호환성 테스트

---

## 🚧 Phase 9: Mastodon Bot 구현 (미착수)

> **주의**: Bot 파일들이 생성되어 있으나 모두 비어있음 (0 바이트)

### Bot Core
- [ ] `bot/reward_bot.py` - 메인 봇 로직
  - [ ] Mastodon.py 라이브러리 통합
  - [ ] 이벤트 리스너 설정
  - [ ] 명령어 처리 시스템
  - [ ] 자동 포스트 스케줄러

### Activity Checker
- [ ] `bot/activity_checker.py` - 활동 체크 시스템
  - [ ] 출석 체크 (하루 2회: 04:00, 16:00)
  - [ ] 연속 출석 보상
  - [ ] 비활동 유저 감지
  - [ ] 휴가 처리 로직

### Command Handler
- [ ] `bot/command_handler.py` - 사용자 명령어 처리
  - [ ] `/내정보` - 잔액, 통계 조회
  - [ ] `/순위` - 랭킹 조회
  - [ ] `/상점` - 아이템 구매
  - [ ] `/도움말` - 명령어 안내
  - [ ] 관리자 전용 명령어

### Database Integration
- [ ] `bot/database.py` - 봇용 DB 헬퍼
  - [ ] 사용자 조회/생성
  - [ ] 거래 기록
  - [ ] 보상 지급
  - [ ] 통계 조회

### Utilities
- [ ] `bot/utils.py` - 유틸리티 함수
  - [ ] 메시지 포맷팅
  - [ ] 에러 핸들링
  - [ ] 로깅 헬퍼
  - [ ] 시간대 처리

---

## 📦 Phase 10: 배포 준비 (진행 예정)

### Docker 구성
- [ ] Dockerfile 작성
- [ ] docker-compose.yml 작성
- [ ] 멀티 스테이지 빌드 설정
- [ ] 환경 변수 관리

### 데이터베이스 관리
- [ ] 데이터베이스 마이그레이션 스크립트
- [ ] 초기 데이터 시드 스크립트
- [ ] 백업/복구 절차 문서화

### 보안
- [ ] 비밀키 관리 (Flask SECRET_KEY)
- [ ] HTTPS 설정 가이드
- [ ] CORS 정책 설정
- [ ] Rate limiting 구현

---

## 🚀 Phase 11: 프로덕션 배포 (계획)

### 인프라 구성
- [ ] 테스트 서버 배포
  - [ ] test.mastodon.example.com (테스트 마스토돈)
  - [ ] test-admin.mastodon.example.com (테스트 관리 웹)
- [ ] 본 서버 배포
  - [ ] mastodon.example.com (본섭 마스토돈)
  - [ ] admin.mastodon.example.com (본섭 관리 웹)

### 역방향 프록시 설정
- [ ] Nginx 또는 Traefik 설정
- [ ] SSL/TLS 인증서 (Let's Encrypt)
- [ ] 도메인별 라우팅 설정

### 모니터링
- [ ] 로깅 시스템 개선
- [ ] 에러 추적 (Sentry 등)
- [ ] 성능 모니터링
- [ ] 알림 시스템 구축

---

## 🔧 Phase 12: 개선 및 유지보수 (계획)

### 기능 추가
- [ ] 대시보드 실시간 업데이트 (WebSocket)
- [ ] 벌크 작업 지원 (다중 사용자 처리)
- [ ] 데이터 내보내기 (CSV, JSON)
- [ ] 고급 필터링 및 검색
- [ ] 관리자 권한 레벨 세분화

### 성능 최적화
- [ ] 데이터베이스 쿼리 최적화
- [ ] 캐싱 레이어 추가 (Redis)
- [ ] 페이지네이션 성능 개선
- [ ] 정적 파일 CDN 설정

### UX 개선
- [ ] 반응형 디자인 개선
- [ ] 다크 모드 지원
- [ ] 키보드 단축키 지원
- [ ] 알림/토스트 메시지 개선

---

## 📊 현재 진행률

| Phase | 상태 | 진행률 |
|-------|------|--------|
| Phase 1: 기본 아키텍처 | ✅ 완료 | 100% |
| Phase 2: 인증 시스템 | ✅ 완료 | 100% |
| Phase 3: 데이터 레이어 | ✅ 완료 | 100% |
| Phase 4: 비즈니스 로직 | ✅ 완료 | 100% |
| Phase 5: API 엔드포인트 | ✅ 완료 | 100% |
| Phase 6: 웹 인터페이스 | ✅ 완료 | 100% |
| Phase 7: 문서화 | ✅ 완료 | 100% |
| Phase 8: DB & 테스트 도구 | ✅ 완료 | 100% |
| **Phase 9: Mastodon Bot 구현** | ❌ **미착수** | **0%** |
| Phase 10: 배포 준비 | 🔄 예정 | 0% |
| Phase 11: 프로덕션 배포 | 📅 계획 | 0% |
| Phase 12: 개선 및 유지보수 | 📅 계획 | 0% |

**전체 진행률: 약 67%** (Admin Web 100% 완료, Bot 미착수)

### 🎯 핵심 완료사항
- ✅ **Admin Web 완전 구현** (2,192줄)
  - Controllers, Services, Repositories, Routes, Templates
  - Discord OAuth 인증, Dashboard, 사용자/경고/휴가/이벤트/아이템 관리
- ✅ **데이터베이스 스크립트** (init_db.py - 377줄)
- ✅ **테스트 도구** (test_all_api.py - 601줄, seed_test_data.py - 534줄)
- ✅ **풍부한 문서** (12개 문서 파일)

### ⚠️ 주요 미완성 사항
- ❌ **Mastodon Bot 구현** (파일만 생성, 코드 없음)
  - bot/reward_bot.py (0 바이트)
  - bot/activity_checker.py (0 바이트)
  - bot/command_handler.py (0 바이트)
  - bot/database.py (0 바이트)
  - bot/utils.py (0 바이트)

---

## 🎯 다음 단계

### 🚨 최우선 과제: Mastodon Bot 구현 (Phase 9)

**Bot은 시스템의 핵심 기능이지만 현재 완전히 비어있습니다!**

1. **bot/reward_bot.py** - 메인 봇 로직
   - Mastodon.py 통합
   - 이벤트 리스닝
   - 자동 포스트 스케줄링

2. **bot/activity_checker.py** - 출석 체크 시스템
   - 하루 2회 출석 체크 (04:00, 16:00)
   - 연속 출석 보상
   - 휴가 처리

3. **bot/command_handler.py** - 명령어 처리
   - 사용자 명령어 (`/내정보`, `/순위`, `/상점`, 등)
   - 관리자 명령어
   - 도움말 시스템

4. **bot/database.py** - DB 헬퍼
   - 사용자 조회/생성
   - 거래 기록
   - 보상 지급

5. **bot/utils.py** - 유틸리티
   - 메시지 포맷팅
   - 에러 핸들링
   - 로깅

### 즉시 착수 가능 (Phase 10 준비)
1. **Admin Web 수동 테스트**
   - 로컬 환경에서 실행
   - DB 초기화 (init_db.py)
   - 테스트 데이터 생성 (seed_test_data.py)
   - API 테스트 (test_all_api.py)

2. **Docker 구성**
   - Dockerfile 작성
   - docker-compose.yml 설정

### 중기 목표 (1-2주)
- Bot 구현 완료 및 테스트
- 실제 Mastodon 서버 연동 테스트
- E2E 통합 테스트
- 배포 스크립트 작성

### 장기 목표 (1개월+)
- 프로덕션 환경 배포
- 모니터링 시스템 구축
- 사용자 피드백 반영 및 개선

---

## 📝 변경 이력

- **2025-11-18 (업데이트)**: 현재 코드 상태 반영
  - Phase 8 완료로 업데이트 (DB 스크립트, 테스트 도구)
  - Phase 9 추가: Mastodon Bot 구현 (미착수)
  - Bot 파일들이 비어있음을 명확히 표시
  - 전체 진행률 67%로 재계산
  - 다음 단계에 Bot 구현을 최우선 과제로 설정
- 2025-11-18: 로드맵 초안 작성, Phase 1-7 완료 반영
