# 마녀봇 (Witch Bot)

휘핑 에디션 마스토돈용 활동량 기반 자동 운영 관리 시스템

## 📊 현재 상태 (2025-11-18)

> ⚠️ **중요**: 이 프로젝트는 현재 **부분 완료** 상태입니다.

### ✅ 완료 (67%)
- **Admin Web** - 100% 구현 완료 (2,192줄)
  - Flask 5-layer 아키텍처
  - Mastodon OAuth 인증
  - 대시보드, 사용자/경고/휴가/이벤트/상점 관리
- **Database** - 스키마 완료 (init_db.py)
- **Testing Tools** - API 테스트, 데이터 생성 스크립트
- **Documentation** - 11개 문서 파일

### ❌ 미구현 (33%)
- **Mastodon Bot** - 0% (모든 파일 0바이트)
  - 재화 지급, 출석 체크, 활동량 감시
  - 사용자/관리자 명령어
  - 자동 포스트 스케줄링
- **Tests** - Unit/Integration/E2E 테스트 없음
- **Deployment** - Docker, systemd 미설정

**다음 단계**: docs/로드맵.md의 "당장 할일" 참고

---

## 개요

마스토돈 커뮤니티를 위한 활동량 기반 자동 관리 시스템. Admin Web으로 사용자를 관리하고, Bot(미구현)으로 자동화된 운영을 수행합니다.

## 핵심 기능

### ✅ Admin Web (구현 완료)
1. **사용자 관리** - 목록, 상세, 재화 조정
2. **경고 관리** - 경고 발송, 내역 조회
3. **휴가 관리** - 신청, 승인/거부
4. **일정 관리** - 이벤트, 전역 휴식기간
5. **상점 관리** - 아이템 CRUD
6. **설정 관리** - 시스템 설정
7. **관리자 로그** - 모든 액션 기록

### ❌ Mastodon Bot (미구현 - Phase 2)
1. 재화 지급 (하루 2회 정산, 오전 4시/오후 4시)
2. 출석 체크 (매일 오전 10시, 자정까지 출석 가능)
3. 활동량 체크 (소셜 분석, 경고 발송)
4. 사용자 명령어 (`@봇 내재화`, `@봇 상점`, `@봇 도움말` 등)
5. 관리자 명령어 (재화 지급/차감, 시스템 상태)
6. 자동 포스트 스케줄링

## 기술 스택
- 마스토돈: Ruby 3.2.2 (휘핑 에디션)
- 봇: Python 3.9+
- 웹: Flask 3.x + Bootstrap 5
- DB: PostgreSQL (마스토돈, 읽기 전용) + SQLite (economy.db)
- 캐시/큐: Redis + Celery
- 인프라: GCP (Google Cloud Platform)

## 프로젝트 구조

```
commumanager/
├── admin_web/              # Flask 관리자 웹 애플리케이션
│   ├── app.py             # 애플리케이션 진입점
│   ├── config.py          # 설정 파일
│   ├── models/            # 데이터 모델 (Model)
│   ├── repositories/      # 데이터베이스 접근 (Repository)
│   ├── services/          # 비즈니스 로직 (Service)
│   ├── controllers/       # 비즈니스 로직 처리 (Controller)
│   ├── routes/            # Flask Blueprint (Route)
│   ├── static/            # 정적 파일 (CSS, JS, 이미지)
│   ├── templates/         # Jinja2 템플릿
│   └── utils/             # 유틸리티 함수
│
├── bot/                   # Mastodon 봇 시스템 ❌ 미구현 (Phase 2 대기 중)
│   ├── reward_bot.py      # 메인 봇 (재화, 출석, 명령어) - 0 bytes
│   ├── activity_checker.py # 활동량 체크 시스템 - 0 bytes
│   ├── command_handler.py # 사용자 명령어 처리 - 0 bytes
│   ├── database.py        # DB 헬퍼 - 0 bytes
│   └── utils.py           # 유틸리티 - 0 bytes
│
├── docs/                  # 프로젝트 문서 (11개)
│   ├── 로드맵.md           # 개발 로드맵 (당장 할일 포함)
│   ├── bot_architecture.md # Bot 구조 (계획)
│   ├── features.md        # 기능 목록 (Admin Web ✅, Bot ❌)
│   ├── use_cases.md       # 유스케이스
│   ├── database.md        # DB 설계 및 ERD
│   ├── admin_oauth.md     # Mastodon OAuth
│   ├── api_design.md      # REST API 설계
│   ├── server_setup.md    # 서버 구축 가이드
│   ├── ADMIN_GUIDE.md     # 관리자 가이드
│   ├── EMERGENCY.md       # 긴급 대응 매뉴얼
│   └── SCREEN_EXAMPLES.md # UI 예시
│
├── .env.example           # 환경 변수 예시
├── .gitignore             # Git 제외 파일 목록
├── requirements.txt       # Python 의존성
└── README.md              # 프로젝트 소개
```

## 백엔드 아키텍처

Flask 관리자 웹은 **Model - Repository - Service - Controller - Route** 5계층 아키텍처를 사용합니다.

```
HTTP Request → Route → Controller → Service → Repository → Database
```

## 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
```

### 4. 데이터베이스 초기화
```bash
python init_db.py economy.db
```

### 5. Flask 개발 서버 실행
```bash
cd admin_web
python app.py
```

## 문서

### 시작하기
- **[개발 로드맵](docs/로드맵.md)** - 당장 할일, 진행 상황 ⭐
- [서버 구축](docs/server_setup.md) - 서버 설치 가이드

### 기능 및 설계
- [기능 목록](docs/features.md) - Admin Web ✅, Bot ❌
- [봇 구조](docs/bot_architecture.md) - Bot 계획 (미구현)
- [유즈케이스](docs/use_cases.md) - 상세 시나리오
- [데이터베이스 설계](docs/database.md) - ERD, 테이블 구조
- [API 설계](docs/api_design.md) - REST API 스펙

### 운영 가이드
- [관리자 가이드](docs/ADMIN_GUIDE.md) - Admin Web 사용법
- [긴급 대응](docs/EMERGENCY.md) - 장애 대응 매뉴얼
- [OAuth 설정](docs/admin_oauth.md) - Mastodon OAuth

### UI
- [화면 예시](docs/SCREEN_EXAMPLES.md) - SVG 목업

## 디렉토리 구조

- `admin_web/` - Flask 관리자 웹
- `bot/` - 마스토돈 봇 시스템
- `docs/` - 프로젝트 문서
