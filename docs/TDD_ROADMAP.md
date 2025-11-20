# TDD 전체 재작성 로드맵

> **전략**: 모든 기존 코드를 백업하고, 순수 TDD(Red → Green → Refactor)로 처음부터 재구축
> **원칙**: Kent Beck의 TDD + Tidy First + 5-Layer Architecture

---

## 📋 목차

- [Phase 0: 프로젝트 초기화](#phase-0-프로젝트-초기화)
- [Phase 1: 코어 도메인 - User & Transaction](#phase-1-코어-도메인---user--transaction)
- [Phase 2: 활동량 관리 - Warning & Vacation](#phase-2-활동량-관리---warning--vacation)
- [Phase 3: 재화 소비 - Item & Shop](#phase-3-재화-소비---item--shop)
- [Phase 4: 일정 관리 - Calendar Events](#phase-4-일정-관리---calendar-events)
- [Phase 5: 예약 발송 - Story Events & Announcements](#phase-5-예약-발송---story-events--announcements)
- [Phase 6: 관리 시스템 - Settings & Admin Logs](#phase-6-관리-시스템---settings--admin-logs)
- [Phase 7: 대시보드 & 통합](#phase-7-대시보드--통합)
- [Phase 8: 인증 & 권한](#phase-8-인증--권한)

---

## Phase 0: 프로젝트 초기화

### 🎯 목표
- 테스트 환경 구축
- DB 초기화 스크립트 작성 (TDD로)
- 개발 환경 설정

### 📦 의존성
- 없음 (시작점)

### 🛠️ 작업 항목

#### 1. 기존 코드 백업
```bash
# admin_web/ 전체를 백업
mv admin_web admin_web_backup_$(date +%Y%m%d)

# 새로운 admin_web/ 디렉토리 생성
mkdir -p admin_web/{models,repositories,services,controllers,routes,templates,static,utils,tests}
```

#### 2. 테스트 프레임워크 설정
```bash
# requirements.txt에 추가
pytest==7.4.3
pytest-cov==4.1.0
pytest-flask==1.3.0
```

**첫 번째 테스트 (Red):**
```python
# tests/test_database.py
def test_should_create_economy_database():
    """economy.db 파일이 생성되어야 한다"""
    # 아직 구현 안 됨 → FAIL
    assert os.path.exists('economy.db')
```

**구현 (Green):**
```python
# init_db.py
def create_database():
    conn = sqlite3.connect('economy.db')
    # ...
```

#### 3. 데이터베이스 스키마 작성 (TDD)

**테스트 순서:**
1. `test_should_create_users_table()`
2. `test_should_create_transactions_table()`
3. `test_should_create_warnings_table()`
4. ... (18개 테이블)

**구현:**
- `init_db.py` - 각 테스트 통과시키며 스키마 추가
- **중요**: `story_events`에 `calendar_event_id` 포함 (문서 기준)

#### 4. 설정 파일 작성
```python
# admin_web/config.py
class Config:
    DATABASE_PATH = 'economy.db'
    MASTODON_DB_PATH = 'mastodon_production'
    SECRET_KEY = os.getenv('SECRET_KEY')
```

### ✅ 완료 기준 (Definition of Done)
- [ ] `pytest` 실행 시 모든 테스트 통과
- [ ] `economy.db` 생성 및 18개 테이블 존재
- [ ] 코드 커버리지 100% (init_db.py)
- [ ] 문서화: `database.md`와 스키마 일치 확인

### ⏱️ 예상 시간
- 2~3시간

---

## Phase 1: 코어 도메인 - User & Transaction

### 🎯 목표
- 유저 CRUD 완성
- 재화 조정 기능
- 거래 내역 관리

### 📦 의존성
- Phase 0 완료 (DB 스키마)

### 🧱 구현할 모델

#### User
```python
# admin_web/models/user.py
@dataclass
class User:
    mastodon_id: str
    username: str
    display_name: Optional[str]
    role: str
    dormitory: Optional[str]
    balance: int
    total_earned: int
    total_spent: int
    reply_count: int
    last_active: Optional[datetime]
    last_check: Optional[datetime]
    created_at: Optional[datetime]
```

#### Transaction
```python
# admin_web/models/transaction.py
@dataclass
class Transaction:
    id: Optional[int]
    user_id: str
    transaction_type: str
    amount: int
    status_id: Optional[str]
    item_id: Optional[int]
    description: Optional[str]
    admin_name: Optional[str]
    timestamp: Optional[datetime]
```

### 🗄️ Repository 메서드 (TDD 순서)

#### UserRepository
```python
# tests/repositories/test_user_repository.py

# 1. Read Operations
def test_should_find_user_by_id()  # → find_by_id()
def test_should_return_none_when_user_not_found()
def test_should_find_all_users_with_pagination()  # → find_all()
def test_should_search_users_by_username()
def test_should_filter_users_by_role()
def test_should_sort_users_by_balance()

# 2. Create Operation
def test_should_create_new_user()  # → create()
def test_should_raise_error_on_duplicate_user()

# 3. Update Operations
def test_should_update_user_role()  # → update_role()
def test_should_update_user_balance()  # → update_balance()
def test_should_increase_balance_and_total_earned()
def test_should_decrease_balance_and_total_spent()
def test_should_not_allow_negative_balance()

# 4. Activity Tracking (PostgreSQL)
def test_should_get_user_activity_48h()  # → get_activity_48h()
def test_should_return_zero_when_no_replies()
```

**구현 순서:**
1. 각 테스트 하나씩 작성 (Red)
2. 최소 코드로 통과 (Green)
3. 중복 제거 (Refactor)

#### TransactionRepository
```python
# tests/repositories/test_transaction_repository.py

def test_should_create_transaction()  # → create()
def test_should_find_transactions_by_user()  # → find_by_user()
def test_should_find_all_transactions_with_filters()  # → find_all()
def test_should_filter_by_type()
def test_should_filter_by_date_range()
def test_should_count_total_transactions()  # → count()
```

### 🧠 Service 로직

#### UserService
```python
# tests/services/test_user_service.py

# 1. 조회 로직
def test_should_get_user_by_id()
def test_should_get_paginated_users()
def test_should_get_user_detail_with_activity()

# 2. 역할 변경
def test_should_change_user_role()
def test_should_validate_role_value()
def test_should_not_change_to_invalid_role()

# 3. 재화 조정 (핵심 로직)
def test_should_adjust_balance_and_create_transaction()
def test_should_increase_total_earned_on_positive_adjustment()
def test_should_increase_total_spent_on_negative_adjustment()
def test_should_not_allow_balance_below_zero()
def test_should_rollback_on_transaction_creation_failure()

# 4. 통계
def test_should_get_user_statistics()
```

**Service 구현 시 주의:**
- 트랜잭션 관리 (balance 업데이트 + transaction 생성)
- 비즈니스 규칙 검증 (음수 잔액 방지)

### 🎮 Controller & API

#### UserController
```python
# tests/controllers/test_user_controller.py

# GET /api/v1/users
def test_should_return_user_list()
def test_should_return_400_on_invalid_page()

# GET /api/v1/users/{id}
def test_should_return_user_detail()
def test_should_return_404_when_user_not_found()

# PATCH /api/v1/users/{id}/role
def test_should_update_user_role()
def test_should_return_400_on_missing_role()
def test_should_return_400_on_invalid_role()

# POST /api/v1/transactions/adjust
def test_should_adjust_user_balance()
def test_should_return_400_on_missing_fields()
def test_should_return_400_on_negative_balance()

# GET /api/v1/users/{id}/transactions
def test_should_return_user_transactions()
def test_should_paginate_transactions()

# GET /api/v1/users/{id}/activity
def test_should_return_user_activity_detail()
def test_should_return_hourly_distribution()
```

#### TransactionController (새로 생성)
```python
# tests/controllers/test_transaction_controller.py

# GET /api/v1/transactions
def test_should_return_all_transactions()
def test_should_filter_by_user_id()
def test_should_filter_by_type()
def test_should_filter_by_date_range()
```

### 📝 API 엔드포인트

```
GET    /api/v1/users                      # 유저 목록
GET    /api/v1/users/{id}                 # 유저 상세
PATCH  /api/v1/users/{id}/role            # 역할 변경
GET    /api/v1/users/{id}/transactions    # 유저 거래 내역
GET    /api/v1/users/{id}/activity        # 유저 활동량 상세 ⭐ 새로 추가
POST   /api/v1/transactions/adjust        # 재화 조정
GET    /api/v1/transactions               # 전체 거래 내역 ⭐ 새로 추가
```

### 🔄 TDD 사이클 예시

**예: UserRepository.find_by_id() 구현**

#### Step 1: Red (실패 테스트)
```python
# tests/repositories/test_user_repository.py
def test_should_find_user_by_id():
    # Given: DB에 유저 삽입
    user = User(mastodon_id='123', username='test_user', role='user')
    # (직접 DB 삽입)

    # When: find_by_id 호출
    found = UserRepository.find_by_id('123')

    # Then: 유저 반환
    assert found is not None
    assert found.mastodon_id == '123'
    assert found.username == 'test_user'
```

**실행 결과:** `AttributeError: 'UserRepository' object has no attribute 'find_by_id'` ❌

#### Step 2: Green (최소 구현)
```python
# admin_web/repositories/user_repository.py
class UserRepository:
    @staticmethod
    def find_by_id(mastodon_id: str) -> Optional[User]:
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE mastodon_id = ?", (mastodon_id,))
            row = cursor.fetchone()
            if row:
                return User(**dict(row))
            return None
```

**실행 결과:** ✅ 통과

#### Step 3: Refactor (중복 제거, 개선)
- `get_economy_db()` 헬퍼 함수 추출
- `dict(row)` → `User` 변환 로직 개선
- 재실행 → 여전히 통과 확인

#### Step 4: 다음 테스트
```python
def test_should_return_none_when_user_not_found():
    found = UserRepository.find_by_id('nonexistent')
    assert found is None
```

**반복...**

### ✅ 완료 기준
- [ ] User 모델 테스트 커버리지 100%
- [ ] Transaction 모델 테스트 커버리지 100%
- [ ] UserRepository 모든 메서드 테스트
- [ ] TransactionRepository 모든 메서드 테스트
- [ ] UserService 비즈니스 로직 테스트
- [ ] UserController API 테스트 (통합)
- [ ] 모든 API 엔드포인트 수동 테스트 성공
- [ ] 커밋: "기능 추가: User & Transaction 완전 구현"

### ⏱️ 예상 시간
- 6~8시간

---

## Phase 2: 활동량 관리 - Warning & Vacation

### 🎯 목표
- 경고 시스템 구현
- 휴식 관리 구현
- 활동량 체크 로직

### 📦 의존성
- Phase 1 완료 (User)

### 🧱 구현할 모델

#### Warning
```python
@dataclass
class Warning:
    id: Optional[int]
    user_id: str
    warning_type: str
    check_period_hours: Optional[int]
    required_replies: Optional[int]
    actual_replies: Optional[int]
    message: Optional[str]
    dm_sent: bool
    admin_name: Optional[str]
    timestamp: Optional[datetime]
```

#### Vacation
```python
@dataclass
class Vacation:
    id: Optional[int]
    user_id: str
    start_date: date
    start_time: Optional[time]
    end_date: date
    end_time: Optional[time]
    reason: Optional[str]
    approved: bool
    registered_by: Optional[str]
    created_at: Optional[datetime]
```

### 🗄️ Repository 메서드 (TDD 순서)

#### WarningRepository
```python
# tests/repositories/test_warning_repository.py

def test_should_create_warning()  # → create()
def test_should_find_warnings_by_user()  # → find_by_user()
def test_should_count_warnings_by_user()  # → count_by_user()
def test_should_find_all_warnings_with_pagination()  # → find_all()
def test_should_filter_by_warning_type()
def test_should_filter_by_date_range()
def test_should_get_statistics()  # → get_statistics() ⭐ 새로 추가
```

**get_statistics() 구현:**
```python
def get_statistics() -> dict:
    """
    Returns:
        {
            'total': 23,
            'this_week': 3,
            'today': 1,
            'by_type': {'activity': 10, 'isolation': 5, ...}
        }
    """
```

#### VacationRepository
```python
# tests/repositories/test_vacation_repository.py

def test_should_create_vacation()  # → create()
def test_should_find_by_user()  # → find_by_user()
def test_should_check_if_user_on_vacation_today()  # → is_user_on_vacation()
def test_should_check_vacation_with_time_range()
def test_should_find_active_vacations()  # → find_active()
def test_should_delete_vacation()  # → delete()
def test_should_get_statistics()  # → get_statistics() ⭐ 새로 추가
```

**is_user_on_vacation() 로직:**
- 현재 시각이 `start_date + start_time` ~ `end_date + end_time` 범위 내인지 확인
- `start_time`이 NULL이면 00:00 기준
- `end_time`이 NULL이면 23:59 기준

### 🧠 Service 로직

#### WarningService
```python
# tests/services/test_warning_service.py

# 1. 경고 생성 및 발송
def test_should_create_warning_and_send_dm()
def test_should_mark_dm_sent_on_success()
def test_should_mark_dm_not_sent_on_failure()

# 2. 경고 조회
def test_should_get_user_warnings()
def test_should_get_all_warnings_with_filters()

# 3. 활동량 체크 (핵심 로직)
def test_should_check_activity_for_all_users()
def test_should_skip_users_on_vacation()
def test_should_skip_admin_users()
def test_should_create_warning_for_below_threshold()
def test_should_not_warn_above_threshold()

# 4. 통계
def test_should_get_warning_statistics()
```

**활동량 체크 로직 (중요):**
```python
# admin_web/services/warning_service.py
def check_activity(period_hours: int, min_replies: int) -> dict:
    """
    1. 설정 로드 (settings 테이블)
    2. PostgreSQL 벌크 조회 (48시간 답글 수)
    3. SQLite users와 매칭
    4. 각 유저별 판정:
       - role이 admin/system/story → 제외
       - 휴식 중 → 제외
       - 답글 < 기준 → 경고 생성
    5. 통계 반환
    """
```

#### VacationService
```python
# tests/services/test_vacation_service.py

def test_should_register_vacation()
def test_should_validate_max_vacation_days()
def test_should_not_allow_overlapping_vacations()
def test_should_cancel_vacation()
def test_should_check_if_vacation_active()
```

### 🎮 Controller & API

#### WarningController
```python
# tests/controllers/test_warning_controller.py

# GET /api/v1/warnings
def test_should_return_all_warnings()
def test_should_filter_by_user()
def test_should_filter_by_type()

# POST /api/v1/warnings
def test_should_create_warning_manually()
def test_should_send_dm_on_creation()

# GET /api/v1/users/{id}/warnings
def test_should_return_user_warnings()
```

#### VacationController
```python
# tests/controllers/test_vacation_controller.py

# GET /api/v1/vacations
def test_should_return_all_vacations()
def test_should_filter_active_vacations()

# POST /api/v1/vacations
def test_should_create_vacation()
def test_should_validate_dates()

# DELETE /api/v1/vacations/{id}
def test_should_delete_vacation()
```

#### ActivityController (새로 생성)
```python
# tests/controllers/test_activity_controller.py

# GET /api/v1/activity/check ⭐ 새로 추가
def test_should_run_activity_check()
def test_should_return_below_threshold_users()
```

### 📝 API 엔드포인트

```
GET    /api/v1/warnings                   # 경고 목록
POST   /api/v1/warnings                   # 경고 발송 (수동)
GET    /api/v1/users/{id}/warnings        # 유저 경고 내역

GET    /api/v1/vacations                  # 휴식 목록
POST   /api/v1/vacations                  # 휴식 등록
DELETE /api/v1/vacations/{id}             # 휴식 해제

GET    /api/v1/activity/check             # 활동량 체크 실행 ⭐ 새로 추가
```

### ✅ 완료 기준
- [ ] Warning 모델 테스트 100%
- [ ] Vacation 모델 테스트 100%
- [ ] WarningRepository 테스트 완료
- [ ] VacationRepository 테스트 완료
- [ ] 활동량 체크 로직 테스트 완료
- [ ] ActivityController 테스트 완료
- [ ] 모든 API 수동 테스트
- [ ] 커밋: "기능 추가: Warning & Vacation 완전 구현"

### ⏱️ 예상 시간
- 6~8시간

---

## Phase 3: 재화 소비 - Item & Shop

### 🎯 목표
- 상점 아이템 관리
- 아이템 구매 로직 (향후 봇 연동)

### 📦 의존성
- Phase 1 완료 (User, Transaction)

### 🧱 구현할 모델

#### Item
```python
@dataclass
class Item:
    id: Optional[int]
    name: str
    description: Optional[str]
    price: int
    category: Optional[str]
    image_url: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
```

#### Inventory (새로 추가)
```python
@dataclass
class Inventory:
    id: Optional[int]
    user_id: str
    item_id: int
    quantity: int
    acquired_at: Optional[datetime]
```

### 🗄️ Repository 메서드

#### ItemRepository
```python
def test_should_create_item()
def test_should_find_all_items()
def test_should_filter_by_category()
def test_should_filter_active_items_only()
def test_should_update_item()
def test_should_deactivate_item()  # soft delete
def test_should_get_statistics()  # ⭐ 새로 추가
```

#### InventoryRepository (새로 생성)
```python
def test_should_add_item_to_inventory()
def test_should_increase_quantity_if_exists()
def test_should_find_user_inventory()
def test_should_check_if_user_owns_item()
```

### 🧠 Service 로직

#### ItemService
```python
def test_should_create_item()
def test_should_validate_price_positive()
def test_should_get_all_items()
def test_should_get_active_items_only()
```

#### ShopService (새로 생성)
```python
# 구매 로직 (트랜잭션)
def test_should_purchase_item()
def test_should_decrease_user_balance()
def test_should_add_to_inventory()
def test_should_create_transaction_record()
def test_should_rollback_on_insufficient_balance()
def test_should_rollback_on_inactive_item()

# 조회
def test_should_get_user_items()
```

### 🎮 Controller & API

```
GET    /api/v1/items                      # 아이템 목록
POST   /api/v1/items                      # 아이템 생성
PUT    /api/v1/items/{id}                 # 아이템 수정
DELETE /api/v1/items/{id}                 # 아이템 비활성화

POST   /api/v1/shop/purchase              # 아이템 구매 (향후 봇 연동)
GET    /api/v1/users/{id}/inventory       # 보유 아이템
```

### ✅ 완료 기준
- [ ] Item, Inventory 모델 테스트 100%
- [ ] ShopService 구매 로직 트랜잭션 테스트
- [ ] API 테스트 완료
- [ ] 커밋: "기능 추가: Item & Shop 완전 구현"

### ⏱️ 예상 시간
- 4~5시간

---

## Phase 4: 일정 관리 - Calendar Events

### 🎯 목표
- 일정/이벤트 관리
- 리뉴얼 기간 설정

### 📦 의존성
- Phase 1 완료 (User)

### 🧱 구현할 모델

#### CalendarEvent
```python
@dataclass
class CalendarEvent:
    id: Optional[int]
    title: str
    description: Optional[str]
    event_date: date
    start_time: Optional[time]
    end_date: Optional[date]
    end_time: Optional[time]
    event_type: str
    is_global_vacation: bool
    created_by: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

### 🗄️ Repository 메서드

```python
def test_should_create_event()
def test_should_find_events_in_date_range()
def test_should_filter_by_event_type()
def test_should_find_global_vacations()
def test_should_check_if_renewal_period()  # is_global_vacation=1인 날짜 확인
def test_should_update_event()
def test_should_delete_event()
def test_should_get_statistics()  # ⭐ 새로 추가
```

### 🧠 Service 로직

```python
def test_should_create_event()
def test_should_validate_date_range()  # end_date >= event_date
def test_should_get_upcoming_events()
def test_should_get_events_until_next_renewal()
```

### 🎮 Controller & API

```
GET    /api/v1/calendar/events            # 일정 목록
POST   /api/v1/calendar/events            # 일정 등록
PUT    /api/v1/calendar/events/{id}       # 일정 수정
DELETE /api/v1/calendar/events/{id}       # 일정 삭제
```

### ✅ 완료 기준
- [ ] CalendarEvent 모델 테스트 100%
- [ ] 날짜 검증 로직 테스트
- [ ] API 테스트
- [ ] 커밋: "기능 추가: Calendar Events 완전 구현"

### ⏱️ 예상 시간
- 3~4시간

---

## Phase 5: 예약 발송 - Story Events & Announcements

### 🎯 목표
- 스토리 이벤트 (여러 포스트 일정 간격 발송)
- 공지 예약 발송

### 📦 의존성
- Phase 4 완료 (CalendarEvent - FK 관계)

### 🧱 구현할 모델

#### StoryEvent
```python
@dataclass
class StoryEvent:
    id: Optional[int]
    title: str
    description: Optional[str]
    calendar_event_id: Optional[int]  # ⭐ FK
    start_time: datetime
    interval_minutes: int
    status: str
    created_by: str
    created_at: Optional[datetime]
    published_at: Optional[datetime]
```

#### StoryPost
```python
@dataclass
class StoryPost:
    id: Optional[int]
    event_id: int
    sequence: int
    content: str
    media_urls: Optional[str]  # JSON 배열
    status: str
    mastodon_post_id: Optional[str]
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    error_message: Optional[str]
```

#### ScheduledAnnouncement
```python
@dataclass
class ScheduledAnnouncement:
    id: Optional[int]
    post_type: str
    content: str
    scheduled_at: datetime
    visibility: str
    is_public: bool
    status: str
    mastodon_scheduled_id: Optional[str]
    created_by: str
    created_at: Optional[datetime]
    published_at: Optional[datetime]
```

### 🗄️ Repository 메서드

#### StoryEventRepository
```python
def test_should_create_event()
def test_should_find_event_with_posts()  # JOIN
def test_should_update_event_status()
def test_should_delete_event_cascade_posts()  # CASCADE
def test_should_get_statistics()  # ⭐ 새로 추가
```

#### StoryPostRepository
```python
def test_should_create_post()
def test_should_calculate_scheduled_at()  # start_time + interval * (seq - 1)
def test_should_find_posts_by_event()
def test_should_update_post_status()
def test_should_delete_post()
```

#### ScheduledAnnouncementRepository
```python
def test_should_create_announcement()
def test_should_find_public_announcements()  # is_public=1
def test_should_find_by_status()
def test_should_get_statistics()  # ⭐ 새로 추가
```

### 🧠 Service 로직

#### StoryEventService
```python
def test_should_create_event_with_posts()  # 트랜잭션
def test_should_validate_calendar_event_fk()
def test_should_calculate_post_scheduled_times()
def test_should_upload_excel_bulk_create()  # Excel 업로드
```

**Excel 업로드 로직:**
- 엑셀 파일 파싱
- 여러 이벤트 + 포스트 일괄 생성
- 트랜잭션 관리 (일부 실패 시 롤백)

#### ScheduledAnnouncementService
```python
def test_should_create_announcement()
def test_should_validate_scheduled_time()  # 과거 시간 방지
```

### 🎮 Controller & API

```
GET    /api/v1/story-events               # 스토리 이벤트 목록
GET    /api/v1/story-events/{id}          # 이벤트 상세 (포스트 포함)
POST   /api/v1/story-events               # 이벤트 생성
POST   /api/v1/story-events/{id}/posts    # 포스트 추가
POST   /api/v1/story-events/bulk-upload   # Excel 업로드 ⭐
PUT    /api/v1/story-events/{id}          # 이벤트 수정
DELETE /api/v1/story-events/{id}          # 이벤트 삭제 (CASCADE)

GET    /api/v1/announcements              # 공지 목록
GET    /api/v1/announcements/{id}         # 공지 상세
POST   /api/v1/announcements              # 공지 생성
PUT    /api/v1/announcements/{id}         # 공지 수정
DELETE /api/v1/announcements/{id}         # 공지 삭제
```

### ✅ 완료 기준
- [ ] StoryEvent, StoryPost, ScheduledAnnouncement 모델 테스트 100%
- [ ] CASCADE 삭제 테스트
- [ ] Excel 업로드 테스트
- [ ] scheduled_at 자동 계산 테스트
- [ ] API 테스트
- [ ] 커밋: "기능 추가: Story Events & Announcements 완전 구현"

### ⏱️ 예상 시간
- 6~7시간

---

## Phase 6: 관리 시스템 - Settings & Admin Logs

### 🎯 목표
- 시스템 설정 관리
- 관리자 액션 로깅

### 📦 의존성
- Phase 1 완료 (모든 Service가 AdminLog 사용)

### 🧱 구현할 모델

#### Setting
```python
@dataclass
class Setting:
    key: str
    value: str
    description: Optional[str]
    updated_at: Optional[datetime]
    updated_by: Optional[str]
```

#### AdminLog
```python
@dataclass
class AdminLog:
    id: Optional[int]
    admin_name: str
    action_type: str
    target_user: Optional[str]
    description: Optional[str]
    details: Optional[str]  # JSON
    timestamp: Optional[datetime]
```

### 🗄️ Repository 메서드

#### SettingRepository
```python
def test_should_get_setting_by_key()
def test_should_get_all_settings()
def test_should_update_setting()
def test_should_record_updated_by()
```

#### AdminLogRepository
```python
def test_should_create_log()
def test_should_find_logs_with_pagination()
def test_should_filter_by_admin()
def test_should_filter_by_action_type()
def test_should_filter_by_date_range()
```

### 🧠 Service 로직

#### SettingService
```python
def test_should_get_setting()
def test_should_get_all_settings()
def test_should_update_setting_and_log()  # AdminLog 기록
```

#### AdminLogService
```python
def test_should_create_log()
def test_should_get_logs_with_filters()
```

### 🎮 Controller & API

```
GET    /api/v1/settings                   # 설정 목록
PUT    /api/v1/settings/{key}             # 설정 변경

GET    /api/v1/admin-logs                 # 관리자 로그 조회
```

### ✅ 완료 기준
- [ ] Setting, AdminLog 모델 테스트 100%
- [ ] 모든 Service에 AdminLog 통합 확인
- [ ] API 테스트
- [ ] 커밋: "기능 추가: Settings & Admin Logs 완전 구현"

### ⏱️ 예상 시간
- 3~4시간

---

## Phase 7: 대시보드 & 통합

### 🎯 목표
- 대시보드 통계 API
- 전체 시스템 통합 테스트

### 📦 의존성
- 모든 Phase 완료

### 🧠 Service 로직

#### DashboardService
```python
def test_should_get_user_statistics()
def test_should_get_currency_statistics()
def test_should_get_activity_statistics()
def test_should_get_warning_statistics()
```

**통계 집계:**
- UserRepository.count_all(), count_active_24h()
- TransactionRepository.sum_all_balances()
- WarningRepository.count_this_week()
- VacationRepository.count_active()

### 🎮 Controller & API

```
GET    /api/v1/dashboard/stats            # 대시보드 통계
```

### 통합 테스트

```python
# tests/integration/test_user_flow.py
def test_complete_user_lifecycle():
    """
    1. 유저 생성
    2. 재화 조정
    3. 아이템 구매
    4. 활동량 체크
    5. 경고 발송
    6. 휴식 등록
    7. 통계 조회
    """
```

### ✅ 완료 기준
- [ ] 대시보드 API 테스트
- [ ] 통합 테스트 작성 및 통과
- [ ] E2E 시나리오 테스트
- [ ] 커밋: "기능 추가: Dashboard & 통합 테스트 완료"

### ⏱️ 예상 시간
- 3~4시간

---

## Phase 8: 인증 & 권한

### 🎯 목표
- OAuth 로그인
- 세션 관리
- 권한 검증

### 📦 의존성
- Phase 1 완료 (User)

### 🎮 Controller & API

#### AuthController
```python
def test_should_redirect_to_oauth()  # POST /auth/login
def test_should_handle_oauth_callback()  # GET /auth/callback
def test_should_create_session()
def test_should_reject_non_admin()
def test_should_logout()  # POST /auth/logout
def test_should_return_current_user()  # GET /auth/me ⭐ 새로 추가
```

### 📝 API 엔드포인트

```
POST   /auth/login                        # OAuth 시작
GET    /auth/callback                     # OAuth 콜백
POST   /auth/logout                       # 로그아웃
GET    /api/v1/auth/me                    # 현재 로그인 정보 ⭐ 새로 추가
```

### ✅ 완료 기준
- [ ] OAuth 플로우 테스트
- [ ] 세션 관리 테스트
- [ ] 권한 검증 데코레이터 테스트
- [ ] `/auth/me` API 테스트
- [ ] 커밋: "기능 추가: 인증 & 권한 완전 구현"

### ⏱️ 예상 시간
- 4~5시간

---

## 📊 전체 요약

| Phase | 목표 | 예상 시간 | 누적 시간 |
|-------|------|----------|----------|
| 0 | 프로젝트 초기화 & 테스트 환경 | 2~3h | 3h |
| 1 | User & Transaction | 6~8h | 11h |
| 2 | Warning & Vacation | 6~8h | 19h |
| 3 | Item & Shop | 4~5h | 24h |
| 4 | Calendar Events | 3~4h | 28h |
| 5 | Story Events & Announcements | 6~7h | 35h |
| 6 | Settings & Admin Logs | 3~4h | 39h |
| 7 | Dashboard & 통합 | 3~4h | 43h |
| 8 | 인증 & 권한 | 4~5h | 48h |

**총 예상 시간: 약 48시간 (6일 풀타임)**

---

## 🎯 TDD 원칙 체크리스트

각 Phase마다 확인:

### Red → Green → Refactor
- [ ] 실패 테스트 먼저 작성 (Red)
- [ ] 최소한의 코드로 통과 (Green)
- [ ] 중복 제거 및 개선 (Refactor)

### Tidy First
- [ ] 구조적 변경과 행위적 변경 분리
- [ ] 구조적 변경 커밋 먼저
- [ ] 행위적 변경 커밋 나중

### 코드 품질
- [ ] 테스트 커버리지 95% 이상
- [ ] 모든 테스트 통과
- [ ] Lint 경고 없음
- [ ] 문서 업데이트 (api_design.md)

### 커밋 규율
- [ ] 작은 단위로 자주 커밋
- [ ] 명확한 커밋 메시지
- [ ] 각 커밋이 독립적으로 작동

---

## 🚀 시작 전 준비

### 1. 백업
```bash
mv admin_web admin_web_backup_$(date +%Y%m%d)
```

### 2. 새 디렉토리 생성
```bash
mkdir -p admin_web/{models,repositories,services,controllers,routes,templates,static,utils,tests}
```

### 3. 테스트 프레임워크 설치
```bash
pip install pytest pytest-cov pytest-flask
```

### 4. Phase 0부터 시작!
```bash
pytest tests/test_database.py -v
```

---

## 📚 참고 자료

- **TDD by Example** (Kent Beck)
- **Tidy First?** (Kent Beck)
- **Working Effectively with Legacy Code** (Michael Feathers)
- **Clean Architecture** (Robert C. Martin)

---

**준비되셨나요? Phase 0부터 시작하시겠어요?** 🚀
