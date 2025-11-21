# CommuManager - 마스토돈 커뮤니티 관리 시스템

## 🚀 빠른 시작

### Docker Compose 사용 (권장)

```bash
# 1. 환경 변수 설정
cp .env.example .env

# 2. SECRET_KEY 및 ADMIN_PASSWORD 설정
python -c "import secrets; print(secrets.token_hex(32))"
# 출력된 값을 .env 파일의 SECRET_KEY에 설정
# ADMIN_PASSWORD도 .env 파일에서 변경하세요 (기본값: admin123)

# 3. Docker Compose로 실행
docker-compose up -d

# 4. 웹 브라우저에서 접속
# http://localhost:5000
```

### 로컬 실행

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export ADMIN_PASSWORD="your-secure-password"  # 기본값: admin123

# 3. 데이터베이스 초기화
python init_db.py

# 4. 앱 실행
python admin_web/app.py
```

## 🔐 기본 로그인 정보

- **사용자명**: admin
- **비밀번호**: admin123 (기본값)

⚠️ **보안 경고**: 프로덕션 환경에서는 반드시 `ADMIN_PASSWORD` 환경 변수를 설정하여 비밀번호를 변경하세요!

**비밀번호 변경 방법:**
- **Docker Compose**: `.env` 파일에서 `ADMIN_PASSWORD=your-secure-password` 설정
- **로컬 실행**: `export ADMIN_PASSWORD="your-secure-password"` 명령 실행

## 📋 주요 기능

- ✅ 유저 관리 (잔액 조정, 경고 관리)
- ✅ 아이템 관리 (상점 시스템)
- ✅ 경고 시스템 (활동량, 고립, 편향, 회피)
- ✅ 휴가 관리
- ✅ 일정 관리
- ✅ 스토리 이벤트 & 공지 예약

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 테스트 커버리지 확인
pytest --cov=admin_web --cov-report=html
```

**총 169개 테스트 통과** ✅

## 🏗️ 아키텍처

```
admin_web/
├── models/          # 데이터 모델
├── repositories/    # DB 접근 계층
├── services/        # 비즈니스 로직
├── controllers/     # API 컨트롤러
├── routes/          # Flask 라우트
├── templates/       # HTML 템플릿
└── utils/           # 유틸리티
```

## 📖 문서

- [관리자 가이드](docs/ADMIN_GUIDE.md)
- [API 문서](docs/api_design.md)
- [DB 스키마](docs/database.md)
- [아키텍처](docs/ARCHITECTURE.md)

## 🐳 Docker 배포

```bash
# 이미지 빌드
docker build -t commumanager:latest .

# 컨테이너 실행
docker run -d -p 5000:5000 \
  -v $(pwd)/economy.db:/app/economy.db \
  --name commumanager \
  commumanager:latest
```

## 📝 라이센스

MIT License
