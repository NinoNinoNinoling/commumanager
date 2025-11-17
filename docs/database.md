# Part 4: 데이터베이스 설계

---

## 1. DB 구조 개요

### 1.1 하이브리드 전략

```
PostgreSQL (마스토돈)     SQLite (경제 시스템)
        │                        │
        │ 읽기 전용               │ 읽기/쓰기
        │                        │
    ┌───┴────┐              ┌────┴─────┐
    │accounts│              │  users   │
    │statuses│              │transactions
    └────────┘              │ warnings │
                            │ settings │
                            │ vacation │
                            │  items   │
                            │inventory │
                            │admin_logs│
                            └──────────┘
```

---

## 2. SQLite 테이블 상세 (economy.db)

### 2.1 users 테이블

**목적**: 유저별 재화 및 역할 관리

```sql
CREATE TABLE users (
    mastodon_id TEXT PRIMARY KEY,      -- 마스토돈 계정 ID
    username TEXT NOT NULL,            -- @username
    display_name TEXT,                 -- 표시 이름
    role TEXT DEFAULT 'user',          -- 역할
    dormitory TEXT,                    -- 기숙사/소속 (대시보드용)
    balance INTEGER DEFAULT 0,         -- 보유 재화
    total_earned INTEGER DEFAULT 0,    -- 누적 획득
    total_spent INTEGER DEFAULT 0,     -- 누적 사용
    reply_count INTEGER DEFAULT 0,     -- 총 답글 수
    last_active TIMESTAMP,             -- 마지막 활동
    last_check TIMESTAMP,              -- 마지막 체크
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_balance ON users(balance DESC);
CREATE INDEX idx_users_last_active ON users(last_active DESC);
CREATE INDEX idx_users_role ON users(role);
```

**role 값**:
- `user`: 일반 유저 (활동량 체크 대상)
- `admin`: 관리자 (체크 제외)
- `system`: 시스템 계정/봇 (체크 제외)
- `story`: 스토리 전용 계정 (체크 제외)

**dormitory**: 선택 필드
- 대시보드에서 "A동", "B동" 등으로 표시
- 소속, 그룹 등 자유롭게 활용

---

### 2.2 transactions 테이블

**목적**: 모든 재화 변동 기록 (감사 추적)

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,    -- 거래 유형
    amount INTEGER NOT NULL,           -- 변동량 (±)
    status_id TEXT,                    -- 답글 status_id (중복 방지)
    item_id INTEGER,                   -- 관련 아이템
    description TEXT,                  -- 설명
    admin_name TEXT,                   -- 관리자 작업 시
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(mastodon_id),
    FOREIGN KEY(item_id) REFERENCES items(id)
);

CREATE INDEX idx_transactions_user ON transactions(user_id, timestamp DESC);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX idx_transactions_status ON transactions(status_id);
```

**transaction_type 값**:
- `earn_reply`: 답글로 획득
- `spend_shop`: 상점 구매
- `game_win`: 게임 승리
- `game_lose`: 게임 패배
- `transfer_send`: 양도 (보낸 쪽)
- `transfer_receive`: 양도 (받은 쪽)
- `admin_add`: 관리자 지급
- `admin_remove`: 관리자 차감

---

### 2.3 warnings 테이블

**목적**: 자동/수동 경고 기록

```sql
CREATE TABLE warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    warning_type TEXT DEFAULT 'auto',  -- 'auto' or 'manual'
    check_period_hours INTEGER,        -- 체크 기간 (48)
    required_replies INTEGER,          -- 요구 답글 수 (20)
    actual_replies INTEGER,            -- 실제 답글 수
    message TEXT,                      -- 수동 경고 메시지
    dm_sent BOOLEAN DEFAULT 0,         -- DM 발송 여부
    admin_name TEXT,                   -- 수동 경고 시 관리자
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
);

CREATE INDEX idx_warnings_user ON warnings(user_id, timestamp DESC);
CREATE INDEX idx_warnings_timestamp ON warnings(timestamp DESC);
CREATE INDEX idx_warnings_type ON warnings(warning_type);
```

---

### 2.4 settings 테이블

**목적**: 모든 시스템 설정 (환경 변수 대체)

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT                    -- 수정한 관리자
);

-- 기본 설정 삽입
INSERT INTO settings (key, value, description) VALUES
('check_times', '05:00,12:00', '활동량 체크 시간 (쉼표 구분)'),
('check_period_hours', '48', '활동량 체크 기간 (시간)'),
('min_replies_48h', '20', '48시간 내 최소 답글 수'),
('replies_per_reward', '1', 'N개 답글당 재화 지급'),
('reward_amount', '10', '지급 재화량'),
('bot_running', 'true', '봇 실행 상태'),
('last_check_5am', '', '마지막 5시 체크 시간'),
('last_check_12pm', '', '마지막 12시 체크 시간');
```

**웹 설정 탭에서 실시간 수정 가능**

---

### 2.5 vacation 테이블

**목적**: 휴식 기간 관리

```sql
CREATE TABLE vacation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,                       -- 사유 (선택)
    registered_by TEXT,                -- 'user' or 관리자명
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
);

CREATE INDEX idx_vacation_user ON vacation(user_id);
CREATE INDEX idx_vacation_dates ON vacation(start_date, end_date);
```

**등록 방법**:
1. 유저: `@봇 휴식 2024-11-25까지`
2. 관리자: 웹에서 수동 등록

**자동 제외**:
```python
def is_on_vacation(user_id):
    today = date.today()
    query = """
    SELECT COUNT(*) FROM vacation
    WHERE user_id = ?
    AND start_date <= ?
    AND end_date >= ?
    """
    return cursor.execute(query, (user_id, today, today)).fetchone()[0] > 0
```

---

### 2.6 items 테이블

**목적**: 상점 아이템 정의

```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                -- 아이템 이름
    description TEXT,                  -- 설명
    price INTEGER NOT NULL,            -- 가격
    category TEXT,                     -- 카테고리
    image_url TEXT,                    -- 이미지 URL (선택)
    is_active BOOLEAN DEFAULT 1,       -- 판매 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_items_active ON items(is_active);
CREATE INDEX idx_items_category ON items(category);
```

**특징**:
- 재고 개념 없음 (무한 구매)
- 효과 없음 (수집용)
- 예시 카테고리:
  - `color`: 닉네임 염색약
  - `border`: 프로필 테두리
  - `badge`: 칭호/뱃지
  - `emote`: 이모트

---

### 2.7 inventory 테이블

**목적**: 유저 보유 아이템

```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(mastodon_id),
    FOREIGN KEY(item_id) REFERENCES items(id),
    UNIQUE(user_id, item_id)           -- 중복 방지
);

CREATE INDEX idx_inventory_user ON inventory(user_id);
CREATE INDEX idx_inventory_item ON inventory(item_id);
```

---

### 2.8 admin_logs 테이블

**목적**: 모든 관리자 작업 기록

```sql
CREATE TABLE admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_name TEXT NOT NULL,
    action_type TEXT NOT NULL,         -- 작업 유형
    target_user TEXT,                  -- 대상 유저
    details TEXT,                      -- JSON 상세 정보
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_logs_timestamp ON admin_logs(timestamp DESC);
CREATE INDEX idx_admin_logs_admin ON admin_logs(admin_name, timestamp DESC);
CREATE INDEX idx_admin_logs_action ON admin_logs(action_type);
```

**action_type 값**:
- `adjust_balance`: 재화 조정
- `send_warning`: 수동 경고
- `register_vacation`: 휴식 등록
- `change_settings`: 설정 변경
- `add_item`: 아이템 추가
- `edit_item`: 아이템 수정
- `delete_item`: 아이템 삭제

---

### 2.9 game_sessions 테이블 (추후)

**목적**: 게임 진행 기록

```sql
CREATE TABLE game_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_type TEXT NOT NULL,           -- 'sutda', 'dice', 'holzzak'
    player_id TEXT NOT NULL,
    opponent_id TEXT,                  -- NULL이면 봇 상대
    bet_amount INTEGER NOT NULL,
    game_state TEXT,                   -- JSON 게임 상태
    winner_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    FOREIGN KEY(player_id) REFERENCES users(mastodon_id)
);

CREATE INDEX idx_game_player ON game_sessions(player_id, finished_at DESC);
CREATE INDEX idx_game_type ON game_sessions(game_type);
```

---

## 3. PostgreSQL 참조 (읽기 전용)

### 3.1 accounts 테이블

**읽기 전용 쿼리**:
```sql
-- 전체 유저 목록
SELECT id, username, display_name, suspended
FROM accounts
WHERE suspended = false;

-- 특정 유저 정보
SELECT id, username, display_name, avatar
FROM accounts
WHERE id = ?;
```

---

### 3.2 statuses 테이블

**읽기 전용 쿼리**:
```sql
-- 48시간 내 답글 수 (벌크)
SELECT 
    u.id,
    u.username,
    COUNT(s.id) as reply_count
FROM accounts u
LEFT JOIN statuses s ON s.account_id = u.id
    AND s.in_reply_to_id IS NOT NULL
    AND s.created_at > NOW() - INTERVAL '48 hours'
WHERE u.suspended = false
GROUP BY u.id, u.username;

-- 특정 유저의 최근 답글
SELECT id, created_at, in_reply_to_id
FROM statuses
WHERE account_id = ?
  AND in_reply_to_id IS NOT NULL
  AND created_at > NOW() - INTERVAL '48 hours'
ORDER BY created_at DESC;
```

---

## 4. DB 초기화 스크립트

### 4.1 init_db.py

```python
import sqlite3

def init_database(db_path='economy.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # users 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            mastodon_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            display_name TEXT,
            role TEXT DEFAULT 'user',
            dormitory TEXT,
            balance INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0,
            total_spent INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            last_active TIMESTAMP,
            last_check TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 인덱스 생성
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
    
    # ... 다른 테이블들 ...
    
    # settings 기본값
    cursor.execute('''
        INSERT OR IGNORE INTO settings (key, value, description) VALUES
        ('check_times', '05:00,12:00', '활동량 체크 시간'),
        ('check_period_hours', '48', '체크 기간'),
        ('min_replies_48h', '20', '최소 답글 수'),
        ('replies_per_reward', '1', '답글당 재화 지급'),
        ('reward_amount', '10', '지급량')
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()
```

---

## 5. 백업 및 마이그레이션

### 5.1 자동 백업

```bash
# /home/ubuntu/backups/backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 /path/to/economy.db ".backup '/backups/economy_$DATE.db'"

# 30일 지난 백업 삭제
find /backups -name "economy_*.db" -mtime +30 -delete
```

### 5.2 데이터 복구

```bash
# 백업에서 복구
cp /backups/economy_20241117.db /path/to/economy.db

# 무결성 체크
sqlite3 economy.db "PRAGMA integrity_check;"
```

---

### 5.3 PostgreSQL → SQLite 마이그레이션

```python
# 초기 유저 동기화
import psycopg2
import sqlite3

def sync_users_from_mastodon():
    # PostgreSQL 연결
    pg_conn = psycopg2.connect(...)
    pg_cur = pg_conn.cursor()
    
    pg_cur.execute("""
        SELECT id, username, display_name
        FROM accounts
        WHERE suspended = false
    """)
    
    # SQLite 연결
    sq_conn = sqlite3.connect('economy.db')
    sq_cur = sq_conn.cursor()
    
    for mastodon_id, username, display_name in pg_cur:
        sq_cur.execute('''
            INSERT OR IGNORE INTO users (mastodon_id, username, display_name)
            VALUES (?, ?, ?)
        ''', (mastodon_id, username, display_name))
    
    sq_conn.commit()
    print(f"Synced {sq_cur.rowcount} users")
```

---

## 다음 문서

→ [Part 5: 관리자 웹 UX](05-admin-web.md)
