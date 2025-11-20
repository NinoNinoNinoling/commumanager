#!/usr/bin/env python3
"""
SQLite 데이터베이스 초기화 스크립트
economy.db 생성 및 초기 데이터 삽입
"""
import sqlite3
import sys
from datetime import datetime


def init_database(db_path='economy.db'):
    """데이터베이스 초기화 및 테이블 생성"""

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    cursor = conn.cursor()

    print(f"📦 데이터베이스 초기화: {db_path}")
    print("=" * 60)

    # 1. users
    cursor.execute("""
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
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
    print("✓ users")

    # 2. transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            status_id TEXT,
            item_id INTEGER,
            description TEXT,
            admin_name TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id, timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status_id)")
    print("✓ transactions")

    # 3. warnings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            warning_type TEXT DEFAULT 'auto',
            check_period_hours INTEGER,
            required_replies INTEGER,
            actual_replies INTEGER,
            message TEXT,
            dm_sent BOOLEAN DEFAULT 0,
            admin_name TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_warnings_user ON warnings(user_id, timestamp DESC)")
    print("✓ warnings")

    # 4. settings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by TEXT
        )
    """)
    print("✓ settings")

    # 5. vacation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            start_date DATE NOT NULL,
            start_time TIME,
            end_date DATE NOT NULL,
            end_time TIME,
            reason TEXT,
            approved BOOLEAN DEFAULT 1,
            registered_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacation_dates ON vacation(start_date, end_date)")
    print("✓ vacation")

    # 6. items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            category TEXT,
            image_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ items")

    # 7. inventory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(mastodon_id),
            FOREIGN KEY(item_id) REFERENCES items(id),
            UNIQUE(user_id, item_id)
        )
    """)
    print("✓ inventory")

    # 8. admin_logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_name TEXT NOT NULL,
            action_type TEXT NOT NULL,
            target_user TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp ON admin_logs(timestamp DESC)")
    print("✓ admin_logs")

    # 9. scheduled_posts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_type TEXT NOT NULL,
            content TEXT NOT NULL,
            scheduled_at TIMESTAMP NOT NULL,
            visibility TEXT DEFAULT 'public',
            is_public BOOLEAN DEFAULT 1,
            status TEXT DEFAULT 'pending',
            mastodon_scheduled_id TEXT,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled ON scheduled_posts(scheduled_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_posts_type ON scheduled_posts(post_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_posts_public ON scheduled_posts(is_public)")
    print("✓ scheduled_posts")

    # 10. attendances
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            attendance_post_id TEXT NOT NULL,
            attended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reward_amount INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(mastodon_id),
            FOREIGN KEY(attendance_post_id) REFERENCES attendance_posts(post_id),
            UNIQUE(user_id, attendance_post_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendances_user ON attendances(user_id, attended_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendances_post ON attendances(attendance_post_id)")
    print("✓ attendances")

    # 11. attendance_posts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT UNIQUE NOT NULL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            total_attendees INTEGER DEFAULT 0
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_posts_posted ON attendance_posts(posted_at DESC)")
    print("✓ attendance_posts")

    # 12. calendar_events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_date DATE NOT NULL,
            start_time TIME,
            end_date DATE,
            end_time TIME,
            event_type TEXT DEFAULT 'event',
            is_global_vacation BOOLEAN DEFAULT 0,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_date ON calendar_events(event_date DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_vacation ON calendar_events(is_global_vacation)")
    print("✓ calendar_events")

    # 13. user_stats
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            unique_conversation_partners INTEGER DEFAULT 0,
            total_replies_sent INTEGER DEFAULT 0,
            top_partner_id TEXT,
            top_partner_username TEXT,
            top_partner_count INTEGER DEFAULT 0,
            top_partner_ratio REAL DEFAULT 0.0,
            active_days_7d INTEGER DEFAULT 0,
            login_rate_7d REAL DEFAULT 0.0,
            is_isolated BOOLEAN DEFAULT 0,
            is_inactive BOOLEAN DEFAULT 0,
            is_biased BOOLEAN DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_stats_user ON user_stats(user_id, analyzed_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_stats_isolated ON user_stats(is_isolated)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_stats_biased ON user_stats(is_biased)")
    print("✓ user_stats")

    # 14. warning_templates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warning_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            warning_type TEXT NOT NULL,
            template TEXT NOT NULL,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(created_by) REFERENCES users(mastodon_id)
        )
    """)
    print("✓ warning_templates")

    # 15. ban_records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ban_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            banned_by TEXT NOT NULL,
            reason TEXT NOT NULL,
            warning_count INTEGER,
            evidence_snapshot TEXT,
            is_active BOOLEAN DEFAULT 1,
            unbanned_at TIMESTAMP,
            unbanned_by TEXT,
            unban_reason TEXT,
            FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ban_records_user ON ban_records(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ban_records_active ON ban_records(is_active)")
    print("✓ ban_records")

    # 16. archived_toots
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archived_toots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            toot_id TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP,
            visibility TEXT,
            in_reply_to_id TEXT,
            in_reply_to_account_id TEXT,
            media_attachments TEXT,
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archived_reason TEXT,
            warning_count_at_archive INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(mastodon_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_archived_toots_user ON archived_toots(user_id, archived_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_archived_toots_toot ON archived_toots(toot_id)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_archived_toots_unique ON archived_toots(user_id, toot_id)")
    print("✓ archived_toots")

    # 17. story_events (스토리 이벤트)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS story_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            interval_minutes INTEGER DEFAULT 5,
            status TEXT DEFAULT 'pending',
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_story_events_start ON story_events(start_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_story_events_status ON story_events(status)")
    print("✓ story_events")

    # 18. story_posts (스토리 개별 포스트)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS story_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            sequence INTEGER NOT NULL,
            content TEXT NOT NULL,
            media_urls TEXT,
            status TEXT DEFAULT 'pending',
            mastodon_post_id TEXT,
            scheduled_at TIMESTAMP,
            published_at TIMESTAMP,
            error_message TEXT,
            FOREIGN KEY(event_id) REFERENCES story_events(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_story_posts_event ON story_posts(event_id, sequence)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_story_posts_status ON story_posts(status)")
    print("✓ story_posts")

    print("=" * 60)
    print("📝 초기 데이터 삽입 중...")

    # settings 초기 데이터
    settings_data = [
        ('timezone', 'Asia/Seoul', '타임존'),
        ('check_period_hours', '48', '조회 기간 (시간)'),
        ('min_replies_48h', '20', '최소 답글 수 기준'),
        ('reward_reply_count', '100', '재화 지급 기준 답글 수'),
        ('reward_per_replies', '10', 'N개당 지급 재화'),
        ('last_reward_settlement_time', '2025-01-01 00:00:00', '마지막 정산 시각'),
        ('attendance_time', '10:00', '출석 트윗 발행 시간'),
        ('attendance_base_reward', '50', '기본 출석 보상'),
        ('attendance_check_enabled', '1', '출석 체크 활성화'),
        ('attendance_tweet_template', '🌟 오늘의 출석 체크!\n이 트윗에 답글 달아주세요!', '출석 트윗 템플릿'),
        ('max_vacation_days', '90', '최대 휴식 기간 (일)'),
        ('vacation_self_service_enabled', '1', '봇 셀프 등록 허용'),
        ('isolation_threshold', '7', '고립 판정 기준 (N명 미만)'),
        ('bias_threshold', '0.3', '편중 판정 기준 (비율)'),
        ('inactive_threshold', '0.5', '비활동 판정 기준 (접속률)'),
        ('archive_warning_threshold', '3', '툿 아카이빙 경고 임계값'),
        ('admin_account', '', '총괄계정명'),
        ('story_account', '', '스토리 계정명'),
        ('system_bot_account', '', '시스템계정명 (@봇)'),
        ('supervisor_bot_account', '', '감독봇 계정명'),
        ('admin_account_id', '', '어드민 마스토돈 계정 ID'),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)",
        settings_data
    )
    print(f"✓ settings: {len(settings_data)}개 항목")

    # warning_templates 초기 데이터
    templates_data = [
        ('활동량 미달', 'activity',
         '@{username}님, 최근 48시간 답글이 {actual_replies}개로 기준({required_replies}개)에 미달했습니다.'),
        ('고립 위험', 'isolation',
         '@{username}님, 최근 대화 상대가 {unique_partners}명으로 적습니다.'),
        ('비활동', 'inactive',
         '@{username}님, 최근 7일 접속률이 {login_rate}%입니다.'),
        ('편중 경고', 'bias',
         '@{username}님, @{top_partner}와의 대화가 {ratio}%입니다.'),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO warning_templates (name, warning_type, template) VALUES (?, ?, ?)",
        templates_data
    )
    print(f"✓ warning_templates: {len(templates_data)}개 템플릿")

    conn.commit()
    conn.close()

    print("=" * 60)
    print("✅ 데이터베이스 초기화 완료!")
    print(f"📍 경로: {db_path}")
    print(f"📊 테이블: 18개")
    print(f"⚙️  설정: {len(settings_data)}개")
    print(f"📋 템플릿: {len(templates_data)}개")


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'economy.db'
    init_database(db_path)
