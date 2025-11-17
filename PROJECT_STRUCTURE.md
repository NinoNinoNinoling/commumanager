# 프로젝트 구조

```
commumanager/
├── admin_web/              # Flask 관리자 웹 애플리케이션
│   ├── app.py             # 애플리케이션 진입점
│   ├── config.py          # 설정 파일
│   ├── __init__.py        # 패키지 초기화
│   ├── models/            # 데이터 모델 (Model)
│   ├── repositories/      # 데이터베이스 접근 (Repository)
│   ├── services/          # 비즈니스 로직 (Service)
│   ├── controllers/       # 비즈니스 로직 처리 (Controller)
│   ├── routes/            # Flask Blueprint (Route)
│   ├── static/            # 정적 파일 (CSS, JS, 이미지)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
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
│   ├── tech_stack.md
│   ├── architecture.md
│   ├── database.md
│   ├── admin web.md
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

#### 1. Model (모델)
- 데이터 구조 정의
- DB 테이블과 매핑되는 객체
- 위치: `admin_web/models/`

#### 2. Repository (저장소)
- 데이터베이스 접근 담당
- SQL 쿼리 실행 및 결과 반환
- Model에 의존
- 위치: `admin_web/repositories/`
- 예시: `user_repository.py` - 유저 데이터 CRUD 작업

#### 3. Service (서비스)
- 복잡한 비즈니스 로직 처리
- Repository를 사용하여 데이터 조작
- 트랜잭션 관리, 유효성 검사
- 위치: `admin_web/services/`
- 예시: `user_service.py` - 유저 관리 로직, 권한 검사

#### 4. Controller (컨트롤러)
- 비즈니스 로직 처리
- Service를 호출하여 로직 수행
- 데이터 변환 및 가공
- 위치: `admin_web/controllers/`
- 예시: `auth_controller.py` - OAuth 처리 로직

#### 5. Route (라우트)
- Flask Blueprint 정의
- HTTP 요청/응답 라우팅
- Controller를 호출
- 위치: `admin_web/routes/`
- 예시: `auth.py` - 인증 관련 엔드포인트

### 데이터 흐름

```
HTTP Request
    ↓
Route (Blueprint 라우팅)
    ↓
Controller (비즈니스 로직)
    ↓
Service (복잡한 비즈니스 로직)
    ↓
Repository (데이터베이스 쿼리)
    ↓
Model (데이터 구조)
    ↓
Database
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
    cursor = conn.execute("SELECT * FROM users WHERE mastodon_id = ?", (mastodon_id,))
    return dict(cursor.fetchone()) if cursor.fetchone() else None
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

### 4. Flask 개발 서버 실행
```bash
cd admin_web
python app.py
```

## 개발 시작하기

- **관리자 웹**: `admin_web/` 디렉토리
- **봇 시스템**: `bot/` 디렉토리
- **문서**: `docs/` 디렉토리

각 디렉토리는 모듈화되어 있으며 독립적으로 개발할 수 있습니다.
