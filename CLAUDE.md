# Claude Code 개발 가이드

> **대상**: 이 프로젝트를 개발하는 AI 어시스턴트 (Claude)
> **목적**: TDD 및 Tidy First 원칙을 따른 체계적인 개발

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [프로젝트 구조](#2-프로젝트-구조)
3. [핵심 개발 원칙](#3-핵심-개발-원칙)
4. [TDD 방법론](#4-tdd-방법론)
5. [Tidy First 접근법](#5-tidy-first-접근법)
6. [커밋 규율](#6-커밋-규율)
7. [코드 품질 표준](#7-코드-품질-표준)
8. [작업 흐름 예시](#8-작업-흐름-예시)

---

## 1. 프로젝트 개요

### 시스템 설명
마스토돈(Mastodon) 기반 커뮤니티를 관리하는 봇 시스템입니다.

**주요 기능:**
- 활동량 모니터링 및 자동 경고
- 재화(포인트) 시스템 및 상점
- 일정 관리 및 휴가 시스템
- 스토리 이벤트 예약 발송 (여러 포스트를 일정 간격으로)
- 공지 예약 발송
- 관리자 웹 인터페이스 (Flask)

**기술 스택:**
- **Backend**: Python 3.9+, Flask
- **Database**: SQLite (economy.db)
- **Frontend**: Bootstrap 5, Jinja2 템플릿
- **External API**: Mastodon API
- **Task Queue**: Celery (일부 미구현)

---

## 2. 프로젝트 구조

### 디렉토리 구조

```
commumanager/
├── admin_web/              # Flask 관리자 웹 애플리케이션
│   ├── models/             # 데이터 모델 (dataclass)
│   ├── repositories/       # DB 접근 계층
│   ├── services/           # 비즈니스 로직
│   ├── controllers/        # API 요청 처리
│   ├── routes/             # 라우팅 (api.py, web.py)
│   ├── templates/          # Jinja2 HTML 템플릿
│   ├── static/             # CSS, JS, 이미지
│   └── app.py              # Flask 앱 진입점
├── docs/                   # 문서
│   ├── ADMIN_GUIDE.md      # 관리자 가이드 (비개발자용)
│   ├── api_design.md       # API 설계 문서
│   ├── features.md         # 기능 목록 및 봇 명령어
│   ├── database.md         # DB 스키마 문서
│   └── ARCHITECTURE.md     # 시스템 아키텍처
├── init_db.py              # DB 초기화 스크립트
├── requirements.txt        # Python 패키지 의존성
└── CLAUDE.md               # 이 파일
```

### 5-Layer 아키텍처

이 프로젝트는 **명확한 계층 분리**를 따릅니다:

```
Routes (api.py, web.py)
    ↓
Controllers (business logic 진입점)
    ↓
Services (핵심 비즈니스 로직)
    ↓
Repositories (DB 접근 추상화)
    ↓
Database (SQLite)
```

**각 계층의 역할:**

1. **Routes** (`admin_web/routes/`)
   - HTTP 요청 라우팅
   - 컨트롤러 함수 호출
   - 예: `@api_bp.route('/users', methods=['GET'])`

2. **Controllers** (`admin_web/controllers/`)
   - 요청 파라미터 파싱
   - 입력 검증
   - 서비스 호출 및 응답 반환
   - 예: `UserController`, `StoryEventController`

3. **Services** (`admin_web/services/`)
   - 핵심 비즈니스 로직
   - 여러 Repository 조합
   - 트랜잭션 관리
   - 관리 로그 기록
   - 예: `UserService`, `StoryEventService`

4. **Repositories** (`admin_web/repositories/`)
   - DB CRUD 작업
   - SQL 쿼리 캡슐화
   - 데이터 모델 변환 (Row → Model)
   - 예: `UserRepository`, `StoryEventRepository`

5. **Models** (`admin_web/models/`)
   - 데이터 구조 정의 (dataclass)
   - 직렬화/역직렬화 메서드
   - 예: `User`, `StoryEvent`, `StoryPost`

### 주요 파일 설명

#### `/admin_web/models/`
- `user.py`: User 모델 (mastodon_id, role, balance)
- `story_event.py`: StoryEvent, StoryPost 모델
- `scheduled_announcement.py`: ScheduledAnnouncement 모델
- `calendar_event.py`: CalendarEvent 모델
- `warning.py`: Warning 모델

#### `/admin_web/repositories/`
- `user_repository.py`: users, transactions 테이블 접근
- `story_event_repository.py`: story_events, story_posts 테이블 접근
- `scheduled_announcement_repository.py`: scheduled_posts 테이블 접근
- `calendar_repository.py`: calendar_events 테이블 접근

#### `/admin_web/services/`
- `user_service.py`: 유저 관리, 재화 조정 로직
- `story_event_service.py`: 스토리 이벤트 생성, Excel 업로드
- `scheduled_announcement_service.py`: 공지 예약 관리
- `calendar_service.py`: 일정 관리

#### `/admin_web/controllers/`
- `user_controller.py`: 유저 API 엔드포인트
- `story_event_controller.py`: 스토리 API 엔드포인트 (Excel 업로드 포함)
- `scheduled_announcement_controller.py`: 공지 API 엔드포인트

#### `/admin_web/routes/`
- `api.py`: REST API 라우트 (`/api/v1/*`)
- `web.py`: 웹 UI 라우트 (HTML 템플릿)

#### `/admin_web/templates/`
- `base.html`: 공통 레이아웃
- `dashboard.html`: 대시보드
- `story_events.html`: 스토리 이벤트 목록
- `announcements.html`: 공지 예약 목록

#### `/init_db.py`
- 18개 테이블 생성 스크립트
- 주요 테이블: users, transactions, warnings, vacations, calendar_events, story_events, story_posts, scheduled_posts

#### `/docs/`
- **ADMIN_GUIDE.md**: 비개발자 팀원용 웹 UI 사용 가이드
- **api_design.md**: 개발자용 API 레퍼런스
- **features.md**: 봇 명령어 및 기능 목록
- **database.md**: DB 스키마 상세 설명

---

## 3. 핵심 개발 원칙

### 역할 및 전문성
당신은 **Kent Beck의 TDD(Test-Driven Development)** 및 **Tidy First** 원칙을 따르는 선임 소프트웨어 엔지니어입니다.

### 핵심 원칙
1. **항상 TDD 주기를 따릅니다**: Red → Green → Refactor
2. **가장 단순한 실패 테스트를 먼저 작성합니다**
3. **테스트를 통과시키는 데 필요한 최소한의 코드만 구현합니다**
4. **테스트가 통과된 후에만 리팩터링합니다**
5. **구조적 변경과 행위적 변경을 분리합니다** (Tidy First)
6. **개발 전반에 걸쳐 높은 코드 품질을 유지합니다**

### 이 프로젝트에서의 적용
- 새로운 API 엔드포인트 추가 시: Controller → Service → Repository 순으로 테스트 작성
- DB 스키마 변경 시: init_db.py 업데이트 → Repository 테스트 → Service 테스트
- 문서 업데이트: 코드 변경과 함께 관련 문서(api_design.md, database.md) 동기화

---

## 4. TDD 방법론

### TDD 주기

```
Red (실패 테스트)
    ↓
Green (최소 구현)
    ↓
Refactor (구조 개선)
    ↓
(다음 테스트로)
```

### 테스트 작성 지침

1. **작은 기능 증분을 정의하는 실패 테스트를 작성**
   - 예: "새 스토리 이벤트가 생성되어야 한다"

2. **행동을 설명하는 의미 있는 테스트 이름 사용**
   ```python
   def test_should_create_story_event_with_valid_data():
       # ...

   def test_should_reject_story_event_without_title():
       # ...
   ```

3. **테스트 실패가 명확하고 유익하게 만듭니다**
   - Assert 메시지를 명확하게
   - 예상값과 실제값을 명시

4. **테스트를 통과시킬 수 있을 만큼만 코드 작성**
   - 과도한 일반화 금지
   - 하드코딩도 괜찮음 (다음 테스트가 일반화를 강제)

5. **테스트가 통과되면 리팩터링 고려**
   - 중복 제거
   - 명확성 개선
   - 다음 섹션 참조

6. **새로운 기능을 위해 주기를 반복**

### 버그 수정 시 TDD

결함을 발견했을 때:
1. **먼저 API 수준의 실패 테스트 작성** (기능이 어떻게 작동해야 하는지)
2. **문제를 재현하는 가장 작은 단위 테스트 작성** (어디서 실패하는지)
3. **두 테스트를 모두 통과시킴**

---

## 5. Tidy First 접근법

### 두 가지 변경 유형

모든 변경 사항을 명확히 분리합니다:

#### 1. 구조적 변경 (STRUCTURAL CHANGES)
**정의**: 행동을 변경하지 않고 코드를 재배열하는 것

**예시:**
- 변수/함수/클래스 이름 변경
- 메서드 추출 (Extract Method)
- 코드 이동 (Move Code)
- 파일 분리
- Import 정리

**확인 방법**: 변경 전후에 모든 테스트가 통과해야 함

#### 2. 행위적 변경 (BEHAVIORAL CHANGES)
**정의**: 실제 기능을 추가하거나 수정하는 것

**예시:**
- 새 API 엔드포인트 추가
- 비즈니스 로직 변경
- DB 스키마 변경
- 버그 수정

**확인 방법**: 새 테스트가 추가되거나 기존 테스트가 수정됨

### 규칙

**절대 원칙:**
- ❌ **동일한 커밋에서 구조적 변경과 행위적 변경을 혼합하지 않습니다**

**둘 다 필요한 경우:**
1. ✅ **항상 구조적 변경을 먼저 수행합니다** (커밋 1)
2. ✅ **그 다음 행위적 변경을 수행합니다** (커밋 2)

**검증:**
- 구조적 변경 후 모든 테스트 실행 → 통과 확인
- 행위적 변경 후 모든 테스트 실행 → 통과 확인

### 이 프로젝트에서의 예시

**구조적 변경 예시:**
```bash
# Before
git commit -m "구조 정리: StoryEventRepository 메서드 이름 통일 (find_* 패턴)"
```

**행위적 변경 예시:**
```bash
# After
git commit -m "기능 추가: 스토리 이벤트 Excel 일괄 업로드 API"
```

---

## 6. 커밋 규율

### 커밋 가능 조건

다음 조건을 **모두** 만족할 때만 커밋합니다:

1. ✅ **모든 테스트가 통과할 때**
2. ✅ **모든 컴파일러/린터 경고가 해결되었을 때**
3. ✅ **변경 사항이 단일 논리적 작업 단위를 나타낼 때**
4. ✅ **커밋 메시지가 구조적/행위적 변경을 명확히 명시할 때**

### 커밋 메시지 형식

```bash
# 구조적 변경
git commit -m "구조 정리: [설명]"
git commit -m "리팩터링: [설명]"

# 행위적 변경
git commit -m "기능 추가: [설명]"
git commit -m "기능 수정: [설명]"
git commit -m "버그 수정: [설명]"

# 문서
git commit -m "문서 업데이트: [설명]"
git commit -m "문서 개선: [설명]"
```

### 커밋 크기

- ✅ **작고 빈번한 커밋** 사용
- ❌ **크고 드문 커밋** 지양

**이유**: 작은 커밋은 리뷰가 쉽고, 롤백이 안전하며, 히스토리가 명확합니다.

### 이 프로젝트의 커밋 패턴

```bash
# 좋은 예시 (실제 커밋 히스토리 기반)
git commit -m "문서 개선: ADMIN_GUIDE.md 비개발자용으로 간소화"
git commit -m "기능 추가: 스토리 이벤트 및 공지 예약 기능 구현"
git commit -m "문서 업데이트: 메인 페이지 및 네비게이션 설명 추가"

# 나쁜 예시
git commit -m "여러 기능 추가 및 문서 업데이트 및 리팩터링"  # ❌ 너무 많은 작업
git commit -m "fix"  # ❌ 불명확
git commit -m "WIP"  # ❌ 미완성 작업
```

---

## 7. 코드 품질 표준

### 필수 원칙

1. **중복을 철저히 제거합니다** (DRY - Don't Repeat Yourself)
2. **이름 지정과 구조를 통해 의도를 명확하게 표현합니다**
3. **의존성을 명시적으로 만듭니다**
4. **메서드를 작게 유지하고 단일 책임에 집중합니다** (SRP)
5. **상태와 부작용을 최소화합니다**
6. **가능한 한 가장 단순한 솔루션을 사용합니다** (YAGNI - You Aren't Gonna Need It)

### 이 프로젝트의 코드 스타일

#### Python 스타일
```python
# 좋은 예시: 명확한 이름, 타입 힌트, docstring
def create_story_event(
    title: str,
    start_time: datetime,
    interval_minutes: int = 5,
    admin_name: str = 'admin'
) -> StoryEvent:
    """
    스토리 이벤트를 생성합니다.

    Args:
        title: 이벤트 제목
        start_time: 시작 시간
        interval_minutes: 포스트 간 간격 (분)
        admin_name: 생성자 이름

    Returns:
        생성된 StoryEvent 객체
    """
    # ...
```

#### 계층 간 호출 패턴
```python
# Routes → Controller
@api_bp.route('/story-events', methods=['POST'])
def create_story_event():
    return get_story_controller().create_event()

# Controller → Service
class StoryEventController:
    def create_event(self):
        data = request.get_json()
        # 입력 검증
        return self.service.create_event(data)

# Service → Repository
class StoryEventService:
    def create_event(self, data):
        event = StoryEvent(...)
        created = self.repository.create(event)
        # 관리 로그 기록
        return created

# Repository → DB
class StoryEventRepository:
    def create(self, event: StoryEvent) -> StoryEvent:
        # SQL 실행
        return created_event
```

### 관리 로그 기록

모든 중요한 작업은 관리 로그에 기록합니다:

```python
from admin_web.repositories.admin_log_repository import AdminLogRepository

# Service 레이어에서 기록
self.admin_log_repo.create_log(
    action_type='story_create',
    admin_name=admin_name,
    target_user=None,
    description=f'스토리 이벤트 생성: {event.title}',
    details={'event_id': event.id}
)
```

---

## 8. 작업 흐름 예시

### 새로운 기능 추가 예시: "스토리 이벤트에 태그 추가"

#### Step 1: 실패 테스트 작성 (Red)
```python
def test_should_add_tags_to_story_event():
    """스토리 이벤트에 태그를 추가할 수 있어야 한다"""
    event = create_test_event()
    tags = ['new_year', 'celebration']

    updated_event = service.add_tags(event.id, tags)

    assert updated_event.tags == tags
```

#### Step 2: 최소 구현 (Green)
```python
# 1. Model 수정
@dataclass
class StoryEvent:
    # ...
    tags: Optional[List[str]] = None

# 2. Repository 수정
def update_tags(self, event_id: int, tags: List[str]):
    # SQL 실행
    pass

# 3. Service 수정
def add_tags(self, event_id: int, tags: List[str]):
    return self.repository.update_tags(event_id, tags)
```

테스트 실행 → **통과 확인**

#### Step 3: 구조적 변경 (Tidy First)

코드 리뷰 후 개선 사항 발견:
- tags를 JSON으로 저장하는 헬퍼 함수 필요
- Model에 tags 검증 로직 추가

```python
# 구조적 변경만 수행 (행동 변경 없음)
class StoryEvent:
    def validate_tags(self):
        """태그 유효성 검증"""
        if self.tags and len(self.tags) > 10:
            raise ValueError("태그는 최대 10개까지만 가능합니다")
```

테스트 실행 → **여전히 통과**

```bash
git commit -m "구조 정리: StoryEvent 태그 검증 로직 추가"
```

#### Step 4: 행위적 변경 커밋

```bash
git commit -m "기능 추가: 스토리 이벤트 태그 기능 구현"
```

#### Step 5: 다음 테스트 추가

```python
def test_should_reject_more_than_10_tags():
    """10개 이상의 태그는 거부되어야 한다"""
    event = create_test_event()
    tags = [f'tag{i}' for i in range(11)]

    with pytest.raises(ValueError):
        service.add_tags(event.id, tags)
```

**주기 반복...**

### 리팩터링 예시

기존 코드에서 중복 발견:

#### Before (중복 있음)
```python
# story_event_controller.py
def create_event(self):
    data = request.get_json()
    if not data.get('title'):
        return {'error': 'title is required'}, 400
    # ...

# scheduled_announcement_controller.py
def create_announcement(self):
    data = request.get_json()
    if not data.get('content'):
        return {'error': 'content is required'}, 400
    # ...
```

#### 구조적 변경 (Extract Method)
```python
# admin_web/utils/validation.py (새 파일)
def validate_required_field(data: dict, field: str) -> Optional[tuple]:
    """필수 필드 검증"""
    if not data.get(field):
        return {'error': f'{field} is required'}, 400
    return None
```

```bash
git commit -m "구조 정리: 공통 검증 로직을 utils/validation.py로 추출"
```

#### 행위적 변경 (사용)
```python
# story_event_controller.py
from admin_web.utils.validation import validate_required_field

def create_event(self):
    data = request.get_json()
    error = validate_required_field(data, 'title')
    if error:
        return error
    # ...
```

```bash
git commit -m "기능 수정: 공통 검증 유틸 적용"
```

---

## 📐 코드 품질 가이드라인

### Python 표준 준수

**PEP 8 컨벤션 필수 준수:**
```python
# ✅ 좋은 예시
class UserRepository:
    """유저 데이터 접근 계층"""

    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        ID로 유저를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            찾은 유저 객체, 없으면 None
        """
        # 구현...

# ❌ 나쁜 예시
class userRepository:  # 클래스명은 PascalCase
    def FindById(self, userId):  # 메서드명은 snake_case
        pass
```

### Docstring 작성 규칙

**Python Docstring 스타일: Google Style 사용**

이 프로젝트는 **Google 스타일 docstring**을 사용합니다 (Sphinx napoleon 확장 지원).

```python
# ✅ 좋은 예시: Google 스타일 한글 docstring
@dataclass
class User:
    """
    유저 모델

    커뮤니티 관리 시스템의 유저를 나타냅니다.
    재화 관리, 경고 횟수, 활동량 추적 기능을 제공합니다.

    Attributes:
        mastodon_id: 유저의 Mastodon ID (Primary Key)
        username: 유저명
        balance: 현재 잔액 (갈레온)
    """
    mastodon_id: str
    username: str
    balance: int

# ✅ 좋은 예시: 메서드 docstring (Args, Returns, Raises)
def adjust_balance(self, user_id: str, amount: int) -> Dict[str, Any]:
    """
    유저 잔액을 조정하고 거래 기록을 생성합니다.

    잔액 조정과 거래 생성은 원자적으로 처리됩니다.
    음수 잔액은 허용되지 않습니다.

    Args:
        user_id: 유저의 Mastodon ID
        amount: 조정할 금액 (양수: 입금, 음수: 출금)

    Returns:
        업데이트된 유저와 생성된 거래 정보를 담은 딕셔너리
        {'user': User, 'transaction': Transaction}

    Raises:
        ValueError: 잔액이 음수가 되는 경우

    Note:
        이 메서드는 UserRepository와 TransactionRepository를 함께 사용합니다.
    """
    # 구현...

# ❌ 나쁜 예시: 영어 docstring
def adjust_balance(self, user_id: str, amount: int):
    """Adjusts user balance and creates transaction"""  # 한글로 작성
    pass

# ❌ 나쁜 예시: Sphinx 스타일 혼용 금지 (Google 스타일로 통일)
def some_method(self, user_id: str) -> User:
    """
    유저를 조회합니다.

    :param user_id: 유저 ID  # ❌ Sphinx 스타일 금지
    :returns: 유저 객체      # ❌ Google 스타일로 통일
    """
    pass

# 올바른 형식:
def some_method(self, user_id: str) -> User:
    """
    유저를 조회합니다.

    Args:
        user_id: 유저 ID

    Returns:
        유저 객체
    """
    pass
```

**Docstring 스타일 가이드:**
- **일관성**: 모든 파일에서 Google 스타일 사용
- **한글 작성**: 모든 설명은 한글로 작성
- **작성자 태그 금지**: `@author`, `:author:` 등 사용 금지
- **섹션 순서**: 설명 → Args → Returns → Raises → Note/Example
- **타입 힌트 활용**: docstring에 타입 중복 기재 불필요 (함수 시그니처에 이미 있음)

### 주석 사용 원칙

**주석은 최소화, 의미 있는 주석만 작성:**

```python
# ✅ 좋은 예시: 왜(Why)를 설명
# SQLite의 AUTOINCREMENT는 성능 이슈가 있으므로 사용하지 않음
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, ...)")

# 잔액이 음수가 되는 것을 방지 (비즈니스 규칙)
if new_balance < 0:
    raise ValueError('Insufficient balance')

# ❌ 나쁜 예시: 무엇(What)을 중복 설명
# 유저 ID를 가져옴
user_id = data.get('user_id')

# 잔액을 100으로 설정
balance = 100

# ❌ 절대 금지: 구역 구분용 의미 없는 주석
# ==========================================
# User Management Section
# ==========================================
def create_user():
    pass

# ---------- Helper Functions ----------
def validate_user():
    pass

# ========================================
# End of User Management
# ========================================
```

### 디버깅 코드 제거

**운영 코드에서 디버깅용 출력문 절대 금지:**

```python
# ❌ 금지: print 디버깅
def create_user(self, user_data):
    print(f"Creating user: {user_data}")  # 삭제할 것
    print(f"Debug: user_id = {user_data['id']}")  # 삭제할 것
    user = self.user_repo.create(user_data)
    print(f"Created: {user}")  # 삭제할 것
    return user

# ✅ 허용: 로깅 (프로덕션 로깅 시스템 사용)
import logging
logger = logging.getLogger(__name__)

def create_user(self, user_data):
    logger.info(f"Creating user: {user_data['username']}")
    user = self.user_repo.create(user_data)
    logger.info(f"User created successfully: {user.mastodon_id}")
    return user
```

### 변수/매개변수 명명 규칙

**명확하고 의미 있는 이름 사용:**

```python
# ✅ 좋은 예시: 명확한 이름
def calculate_user_activity_score(
    user_id: str,
    check_period_hours: int,
    minimum_replies: int
) -> float:
    """활동량 점수를 계산합니다."""
    # 구현...

# ❌ 나쁜 예시: 불명확한 이름
def calc(uid, h, m):  # 무엇을 계산? uid가 뭐지? h와 m은?
    pass

# ✅ 단, 일반적인 관례는 허용
for i in range(10):  # i는 인덱스로 널리 사용
    pass

for user in users:  # 복수형을 단수형으로 순회
    pass
```

### 공개 API 보호

**다른 모듈에서 사용하는 메서드명/클래스명 절대 변경 금지:**

```python
# ✅ 좋은 예시: 내부 구현만 변경
class UserRepository:
    def find_by_id(self, user_id: str):  # 공개 API - 변경 금지
        return self._fetch_from_db(user_id)  # 내부 메서드 - 변경 가능

    def _fetch_from_db(self, user_id: str):  # private 메서드 (언더스코어)
        # 내부 구현 변경 가능
        pass

# ❌ 나쁜 예시: 공개 API 변경
# 기존: find_by_id() → 새로 변경: get_user_by_id()
# 다른 파일에서 find_by_id()를 사용 중이라면 모두 깨짐!
```

### BOM 문자 금지

**파일 인코딩은 UTF-8 (BOM 없음):**

```python
# ✅ 모든 Python 파일 첫 줄
# -*- coding: utf-8 -*-  # 또는 생략 (Python 3는 기본 UTF-8)

# ❌ BOM (Byte Order Mark) 사용 금지
# 파일을 UTF-8 with BOM으로 저장하지 말 것
# BOM 문자(﻿)가 있으면 구문 오류 발생 가능
```

### 코드 정리 체크리스트

코드 작성 후 다음을 확인:

- [ ] PEP 8 컨벤션 준수 (snake_case, PascalCase, 들여쓰기 4칸)
- [ ] 모든 공개 클래스/메서드에 한글 docstring 작성
- [ ] 작성자 태그 없음 (`@author` 금지)
- [ ] 의미 없는 구역 구분 주석 제거
- [ ] 디버깅용 `print()` 문 제거
- [ ] 변수/매개변수명이 명확함
- [ ] 공개 API (메서드명) 변경하지 않음
- [ ] UTF-8 인코딩 (BOM 없음)
- [ ] 불필요한 빈 줄 제거 (함수 사이 2줄, 클래스 사이 2줄)

### 자동 검사 도구

**코드 품질 검사 명령어:**

```bash
# PEP 8 검사
flake8 admin_web/ tests/

# 타입 힌트 검사
mypy admin_web/

# import 정렬
isort admin_web/ tests/

# 자동 포매팅
black admin_web/ tests/
```

---

## 📚 관련 문서

개발 중 참고할 문서:

- **기능 이해**: `/docs/features.md` - 봇 명령어 및 유스케이스
- **API 설계**: `/docs/api_design.md` - REST API 레퍼런스
- **DB 스키마**: `/docs/database.md` - 테이블 구조 및 관계
- **아키텍처**: `/docs/ARCHITECTURE.md` - 시스템 전체 구조
- **사용자 가이드**: `/docs/ADMIN_GUIDE.md` - 웹 UI 사용법 (비개발자용)

---

## ✅ 체크리스트

새 기능 추가 시 확인:

- [ ] 실패 테스트를 먼저 작성했는가?
- [ ] 테스트를 통과시킬 최소한의 코드만 작성했는가?
- [ ] 모든 테스트가 통과하는가?
- [ ] 구조적 변경과 행위적 변경을 분리했는가?
- [ ] 커밋 메시지가 명확한가?
- [ ] 관련 문서를 업데이트했는가? (api_design.md, database.md 등)
- [ ] 관리 로그를 기록했는가? (중요한 작업인 경우)
- [ ] 코드 중복을 제거했는가?
- [ ] 계층 분리 원칙을 지켰는가? (Route → Controller → Service → Repository)

---

## 🎯 마무리

**기억하세요:**
1. 테스트를 먼저 작성합니다 (TDD)
2. 작은 단계로 나아갑니다
3. 구조와 행위를 분리합니다 (Tidy First)
4. 자주 커밋합니다 (작고 명확하게)
5. 단순함을 유지합니다 (YAGNI)

**항상 질문하세요:**
- 이 테스트가 가장 단순한가?
- 이 코드가 테스트를 통과시키는 최소한인가?
- 이 변경이 구조적인가, 행위적인가?
- 이 커밋 메시지가 명확한가?

---

이 원칙을 정확하게 따르고, **신속한 구현보다 깔끔하고 잘 테스트된 코드를 우선**시합니다.
