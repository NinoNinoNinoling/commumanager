# 마녀봇 (Witch Bot)

휘핑 에디션 마스토돈용 활동량 기반 자동 운영 관리 시스템

## 개요

마스토돈 커뮤니티를 위한 활동량 기반 자동 관리 봇. 답글 감지로 재화를 지급하고, 활동량을 체크하여 경고를 발송합니다.

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
- [프로젝트 개요](docs/project_overview.md)
- [기능 목록](docs/features.md)
- [데이터베이스](docs/database.md)
- [서버 구축](docs/server_setup.md)
- [개발 로드맵](docs/로드맵.md)

## 디렉토리 구조

- `admin_web/` - Flask 관리자 웹
- `bot/` - 마스토돈 봇 시스템
- `docs/` - 프로젝트 문서
