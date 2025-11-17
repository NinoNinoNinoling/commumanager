# 프로젝트 구조

```
commumanager/
├── admin_web/              # Flask 관리자 웹 애플리케이션
│   ├── app.py             # 애플리케이션 진입점
│   ├── config.py          # 설정 파일
│   ├── __init__.py        # 패키지 초기화
│   ├── models/            # 데이터 모델
│   ├── routes/            # 라우트 모듈
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
