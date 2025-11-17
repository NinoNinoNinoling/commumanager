# 프로젝트 구조

```
commumanager/
├── admin_web/              # Flask 관리자 웹 애플리케이션
│   ├── app.py             # 애플리케이션 진입점
│   ├── config.py          # 설정 파일
│   ├── __init__.py        # 패키지 초기화
│   ├── models/            # 데이터 모델 (Model)
│   ├── dao/               # 데이터 접근 객체 (DAO)
│   ├── services/          # 비즈니스 로직 (Service)
│   ├── controllers/       # HTTP 요청/응답 처리 (Controller)
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

### Model - DAO - Service - Controller 패턴

Flask 관리자 웹은 4계층 아키텍처를 사용합니다:

#### 1. Model (모델)
- 데이터 구조 정의
- DB 테이블과 매핑되는 객체
- 위치: `admin_web/models/`

#### 2. DAO (Data Access Object)
- 데이터베이스 접근 담당
- SQL 쿼리 실행 및 결과 반환
- Model에 의존
- 위치: `admin_web/dao/`
- 예시: `user_dao.py` - 유저 데이터 CRUD 작업

#### 3. Service (서비스)
- 비즈니스 로직 처리
- DAO를 사용하여 데이터 조작
- 트랜잭션 관리, 유효성 검사
- 위치: `admin_web/services/`
- 예시: `user_service.py` - 유저 관리 로직, 권한 검사

#### 4. Controller (컨트롤러)
- HTTP 요청/응답 처리
- Service를 호출하여 로직 수행
- 템플릿 렌더링 또는 JSON 반환
- Flask Blueprint 사용
- 위치: `admin_web/controllers/`
- 예시: `user_controller.py` - 유저 관련 엔드포인트

### 데이터 흐름

```
HTTP Request
    ↓
Controller (요청 검증, 파라미터 추출)
    ↓
Service (비즈니스 로직 수행)
    ↓
DAO (데이터베이스 쿼리)
    ↓
Model (데이터 구조)
    ↓
Database
```

### 예시: 유저 조회

```python
# Controller (user_controller.py)
@user_bp.route('/<int:user_id>')
def get_user(user_id):
    user = user_service.get_user_info(user_id)
    return render_template('users/detail.html', user=user)

# Service (user_service.py)
def get_user_info(self, user_id):
    return self.user_dao.get_user_by_id(user_id)

# DAO (user_dao.py)
def get_user_by_id(self, user_id):
    cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
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
