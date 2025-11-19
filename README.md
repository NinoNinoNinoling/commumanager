# 마녀봇 (Witch Bot)

휘핑 에디션 마스토돈용 활동량 기반 자동 운영 관리 시스템

## 개요

마스토돈 커뮤니티를 위한 활동량 기반 자동 관리 봇. 답글 감지로 재화를 지급하고, 활동량을 체크하여 경고를 발송합니다.

## 핵심 기능
1. 재화 지급 (하루 2회 정산, 오전 4시/오후 4시)
2. 출석 체크 (매일 오전 10시, 자정까지 출석 가능)
3. 활동량 체크 (소셜 분석, 경고 발송)
4. 휴식 관리 (활동량 체크 제외)
5. 일정 관리 (이벤트, 전역 휴식기간)
6. 상점 시스템 (아이템 구매)

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
├── bot/                   # 관리 봇 시스템 (4개 계정)
│   ├── admin_bot.py       # 총괄계정 (팔로우 등록, 공지)
│   ├── story_bot.py       # 스토리계정 (콘텐츠 발행)
│   ├── system_bot.py      # 시스템계정 (재화, 출석, 명령어)
│   ├── supervisor_bot.py  # 감독봇 (분석, 경고, 알림)
│   ├── database.py        # 데이터베이스 유틸
│   └── utils.py           # 봇 유틸리티
│
├── docs/                  # 프로젝트 문서
│   ├── ADMIN_GUIDE.md      # 관리자 웹 가이드
│   ├── ARCHITECTURE.md     # 시스템 아키텍처
│   ├── features.md         # 기능 목록 및 유즈케이스
│   ├── database.md         # 데이터베이스 설계
│   ├── api_design.md       # API 설계
│   ├── server_setup.md     # 서버 구축 가이드
│   ├── DOCKER_GUIDE.md     # Docker 배포 가이드
│   ├── MAINTENANCE.md      # 유지보수 시스템
│   ├── EMERGENCY.md        # 긴급 대응 절차
│   └── 로드맵.md            # 개발 로드맵
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

### 🐳 Docker 사용 (권장)

**빠른 시작:**
```bash
# 1. 환경 변수 설정
cp .env.docker .env
nano .env  # 실제 값 입력

# 2. 실행
./scripts/docker/start.sh
```

**관리:**
```bash
# 로그 확인
./scripts/docker/logs.sh

# 중지
./scripts/docker/stop.sh

# 재시작
./scripts/docker/restart.sh
```

**자세한 내용:** [Docker 가이드](docs/DOCKER_GUIDE.md)

---

### 💻 로컬 개발 환경

#### 1. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

#### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
```

#### 4. 데이터베이스 초기화
```bash
python init_db.py economy.db
```

#### 5. Redis 실행
```bash
# macOS (Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

#### 6. Flask 개발 서버 실행
```bash
cd admin_web
python app.py
```

#### 7. 봇 실행
```bash
# 새 터미널에서
python -m bot.reward_bot
```

#### 8. Celery 실행
```bash
# 새 터미널에서 Worker 실행
celery -A bot.tasks worker --loglevel=info

# 새 터미널에서 Beat 실행 (스케줄러)
celery -A bot.tasks beat --loglevel=info
```

## 문서

### 🚀 시작하기
- **[Docker 가이드](docs/DOCKER_GUIDE.md)** ⭐ - 프로덕션 배포
- [서버 구축](docs/server_setup.md) - 수동 설치 가이드

### 📖 시스템 이해
- **[시스템 아키텍처](docs/ARCHITECTURE.md)** - 전체 시스템 구조 및 기술 스택
- [기능 목록](docs/features.md) - 모든 기능 및 유즈케이스
- [데이터베이스 설계](docs/database.md) - DB 스키마 및 설계
- [API 설계](docs/api_design.md) - API 엔드포인트

### 👨‍💼 관리자용
- **[관리자 가이드](docs/ADMIN_GUIDE.md)** - 웹 인터페이스 사용법
- **[유지보수 시스템](docs/MAINTENANCE.md)** 🔧 - 자동 유지보수
- **[긴급 대응](docs/EMERGENCY.md)** 🚨 - 트러블슈팅

### 📅 개발 계획
- [개발 로드맵](docs/로드맵.md) - 향후 개발 계획

## 테스트

```bash
# pytest 실행
pytest

# 커버리지와 함께 실행
pytest --cov=admin_web --cov=bot

# 특정 테스트만 실행
pytest tests/test_repositories.py
pytest tests/test_services.py
pytest tests/test_api.py
```

## 디렉토리 구조

- `admin_web/` - Flask 관리자 웹
- `bot/` - 마스토돈 봇 시스템
- `docs/` - 프로젝트 문서
