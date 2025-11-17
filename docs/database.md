# 데이터베이스 설계

## DB 전략

```mermaid
graph LR
    A[PostgreSQL<br/>마스토돈] -->|읽기 전용| B[Economy Bot]
    B -->|읽기/쓰기| C[SQLite<br/>economy.db]
    C -->|읽기| D[Admin Web]
```

## ERD

```mermaid
erDiagram
    users ||--o{ transactions : has
    users ||--o{ warnings : receives
    users ||--o{ vacation : takes
    users ||--o{ inventory : owns
    items ||--o{ inventory : in
    items ||--o{ transactions : relates

    users {
        text mastodon_id PK
        text username
        text display_name
        text role
        text dormitory
        int balance
        int total_earned
        int total_spent
        int reply_count
        timestamp last_active
        timestamp last_check
    }

    transactions {
        int id PK
        text user_id FK
        text transaction_type
        int amount
        text status_id
        int item_id FK
        text description
        text admin_name
        timestamp timestamp
    }

    warnings {
        int id PK
        text user_id FK
        text warning_type
        int check_period_hours
        int required_replies
        int actual_replies
        text message
        bool dm_sent
        text admin_name
        timestamp timestamp
    }

    vacation {
        int id PK
        text user_id FK
        date start_date
        date end_date
        text reason
        text registered_by
    }

    items {
        int id PK
        text name
        text description
        int price
        text category
        text image_url
        bool is_active
    }

    inventory {
        int id PK
        text user_id FK
        int item_id FK
        int quantity
        timestamp acquired_at
    }

    settings {
        text key PK
        text value
        text description
        text updated_by
    }

    admin_logs {
        int id PK
        text admin_name
        text action_type
        text target_user
        text details
        timestamp timestamp
    }

    scheduled_posts {
        int id PK
        text account_username
        text content
        timestamp scheduled_at
        text visibility
        text status
        text mastodon_scheduled_id
        text created_by
        timestamp published_at
    }
```

## SQLite 테이블 (economy.db)

### users
```sql
CREATE TABLE users (
    mastodon_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    display_name TEXT,
    role TEXT DEFAULT 'user',        -- user/admin/system/story
    dormitory TEXT,
    balance INTEGER DEFAULT 0,
    total_earned INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    last_active TIMESTAMP,
    last_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_balance ON users(balance DESC);
CREATE INDEX idx_users_role ON users(role);
```

### transactions
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,  -- earn_reply/spend_shop/admin_add 등
    amount INTEGER NOT NULL,
    status_id TEXT,                  -- 중복 방지용
    item_id INTEGER,
    description TEXT,
    admin_name TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
);
CREATE INDEX idx_transactions_user ON transactions(user_id, timestamp DESC);
CREATE INDEX idx_transactions_status ON transactions(status_id);
```

### warnings
```sql
CREATE TABLE warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    warning_type TEXT DEFAULT 'auto',  -- auto/manual
    check_period_hours INTEGER,
    required_replies INTEGER,
    actual_replies INTEGER,
    message TEXT,
    dm_sent BOOLEAN DEFAULT 0,
    admin_name TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
);
CREATE INDEX idx_warnings_user ON warnings(user_id, timestamp DESC);
```

### settings
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);

-- 기본값
INSERT INTO settings (key, value, description) VALUES
('check_times', '04:00,16:00', '활동량 체크 시간 (12시간 간격)'),
('check_period_hours', '48', '체크 기간'),
('min_replies_48h', '20', '최소 답글 수'),
('replies_per_reward', '1', '답글당 재화'),
('reward_amount', '10', '지급량');
```

### vacation
```sql
CREATE TABLE vacation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    registered_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
);
CREATE INDEX idx_vacation_dates ON vacation(start_date, end_date);
```

### items
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    category TEXT,
    image_url TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### inventory
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(mastodon_id),
    FOREIGN KEY(item_id) REFERENCES items(id),
    UNIQUE(user_id, item_id)
);
```

### admin_logs
```sql
CREATE TABLE admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_name TEXT NOT NULL,
    action_type TEXT NOT NULL,  -- adjust_balance/send_warning/change_settings 등
    target_user TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_admin_logs_timestamp ON admin_logs(timestamp DESC);
```

### scheduled_posts (스토리/공지 예약)
```sql
CREATE TABLE scheduled_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_username TEXT NOT NULL,     -- 스토리/공지 계정명
    content TEXT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    visibility TEXT DEFAULT 'public',   -- public/unlisted/private
    status TEXT DEFAULT 'pending',      -- pending/published/cancelled
    mastodon_scheduled_id TEXT,         -- 마스토돈 예약 ID
    created_by TEXT NOT NULL,           -- 작성한 관리자
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);
CREATE INDEX idx_scheduled_posts_scheduled ON scheduled_posts(scheduled_at);
CREATE INDEX idx_scheduled_posts_status ON scheduled_posts(status);
```

### game_sessions (추후)
```sql
CREATE TABLE game_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_type TEXT NOT NULL,
    player_id TEXT NOT NULL,
    opponent_id TEXT,
    bet_amount INTEGER NOT NULL,
    game_state TEXT,
    winner_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    FOREIGN KEY(player_id) REFERENCES users(mastodon_id)
);
```

## PostgreSQL 참조 (읽기 전용)

### 48시간 답글 수 조회 (벌크)
```sql
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
```

## 백업
```bash
# 매일 3시 SQLite 백업
0 3 * * * sqlite3 /path/to/economy.db ".backup '/backups/economy_$(date +\%Y\%m\%d).db'"

# 30일 지난 백업 삭제
0 6 * * 0 find /backups -name "*.db" -mtime +30 -delete
```

## 초기화
```bash
python3 init_db.py
```
