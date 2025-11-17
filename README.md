# 마녀봇 (Witch Bot)

휘핑 에디션 마스토돈용 활동량 기반 자동 운영 관리 시스템

## 개요
- 30~50명 규모 폐쇄형 커뮤니티
- 답글 기반 재화 지급
- 활동량 자동 체크 및 경고
- 상점 시스템

## 핵심 기능
1. 활동량 체크 (하루 2회, 오전 4시/오후 4시)
2. 재화 지급 (실시간 답글 감지)
3. 상점 시스템 (아이템 구매)
4. 휴식계 (활동량 체크 제외)

## 기술 스택
- 마스토돈: Ruby 3.2.2
- 봇: Python 3.9+
- 웹: Flask 3.x + Bootstrap 5
- DB: PostgreSQL + SQLite
- 캐시/큐: Redis + Celery
- 인프라: 오라클 클라우드 (무료)

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
├── bot/                   # 관리 봇 시스템
│   ├── reward_bot.py      # 재화 지급 봇
│   ├── activity_checker.py # 활동량 체크 봇
│   ├── command_handler.py # 명령어 처리기
│   ├── database.py        # 데이터베이스 유틸
│   └── utils.py           # 봇 유틸리티
│
├── docs/                  # 프로젝트 문서
│   ├── project_overview.md
│   ├── features.md
│   ├── database.md
│   ├── server_setup.md
│   └── 로드맵.md
│
├── .env.example           # 환경 변수 예시
├── .gitignore             # Git 제외 파일 목록
├── requirements.txt       # Python 의존성
└── README.md              # 프로젝트 소개
```

## 백엔드 아키텍처

### Model - Repository - Service - Controller - Route 패턴

Flask 관리자 웹은 5계층 아키텍처를 사용합니다:

1. **Model** - 데이터 구조 정의
2. **Repository** - 데이터베이스 접근 (SQL 쿼리)
3. **Service** - 복잡한 비즈니스 로직, 트랜잭션 관리
4. **Controller** - 비즈니스 로직 처리
5. **Route** - Flask Blueprint 라우팅

### 데이터 흐름

```
HTTP Request → Route → Controller → Service → Repository → Database
```

### 예시: OAuth 로그인

```python
# Route (auth.py)
@auth_bp.route('/login')
def login():
    return auth_controller.login()

# Controller (auth_controller.py)
def login(self):
    mastodon = self.get_mastodon_client()
    auth_url = mastodon.auth_request_url(...)
    return redirect(auth_url)

# Service (user_service.py)
def get_or_create_user(self, mastodon_id, ...):
    user = self.user_repository.get_user_by_mastodon_id(mastodon_id)
    if not user:
        user_id = self.user_repository.create_user(...)
    return user

# Repository (user_repository.py)
def get_user_by_mastodon_id(self, mastodon_id):
    cursor = conn.execute("SELECT * FROM users WHERE mastodon_id = ?", ...)
    return dict(cursor.fetchone())
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
- [프로젝트 개요](docs/project_overview.md)
- [기능 목록](docs/features.md)
- [데이터베이스](docs/database.md)
- [서버 구축](docs/server_setup.md)
- [개발 로드맵](docs/로드맵.md)

## 개발 시작하기

- **관리자 웹**: `admin_web/` 디렉토리
- **봇 시스템**: `bot/` 디렉토리
- **문서**: `docs/` 디렉토리

각 디렉토리는 모듈화되어 있으며 독립적으로 개발할 수 있습니다.
