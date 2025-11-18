#!/usr/bin/env python3
"""
SQLite 데이터베이스 초기화 스크립트
관리 시스템 전용 DB (economy.db) 생성
"""
import sqlite3
import os
from datetime import datetime


def init_database(db_path='economy.db'):
    """
    데이터베이스 초기화 및 테이블 생성

    Args:
        db_path: 데이터베이스 파일 경로
    """
    # 기존 DB 백업
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(db_path, backup_path)
        print(f"기존 DB 백업: {backup_path}")

    # 연결 생성
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")  # 외래키 제약 활성화
    conn.execute("PRAGMA journal_mode = WAL")  # WAL 모드 (동시 읽기/쓰기)
    cursor = conn.cursor()

    print("데이터베이스 테이블 생성 중...")

    # 1. users 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mastodon_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            display_name TEXT,
            is_admin BOOLEAN DEFAULT 0,
            currency INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ users 테이블 생성")

    # 2. transactions 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            related_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("✓ transactions 테이블 생성")

    # 3. warnings 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            reply_count INTEGER,
            threshold INTEGER,
            period_hours INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("✓ warnings 테이블 생성")

    # 4. vacation 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            reason TEXT,
            approved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("✓ vacation 테이블 생성")

    # 5. items 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            category TEXT,
            image_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            stock INTEGER DEFAULT -1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ items 테이블 생성")

    # 6. inventory 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            UNIQUE(user_id, item_id)
        )
    """)
    print("✓ inventory 테이블 생성")

    # 7. system_config 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ system_config 테이블 생성")

    # 8. scheduled_posts 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            scheduled_at TIMESTAMP NOT NULL,
            posted BOOLEAN DEFAULT 0,
            posted_at TIMESTAMP,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
        )
    """)
    print("✓ scheduled_posts 테이블 생성")

    # 9. admin_logs 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("✓ admin_logs 테이블 생성")

    # 10. user_stats 테이블 (소셜 분석)
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
    print("✓ user_stats 테이블 생성")

    # 11. warning_templates 테이블
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
    print("✓ warning_templates 테이블 생성")

    # 12. ban_records 테이블
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
    print("✓ ban_records 테이블 생성")

    # 13. archived_toots 테이블
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
    print("✓ archived_toots 테이블 생성")

    # 인덱스 생성
    print("\n인덱스 생성 중...")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_mastodon_id ON users(mastodon_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_warnings_user_id ON warnings(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacation_user_id ON vacation(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacation_dates ON vacation(start_date, end_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_user_id ON inventory(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_at ON scheduled_posts(scheduled_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id ON admin_logs(admin_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_created_at ON admin_logs(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_stats_user ON user_stats(user_id, analyzed_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_stats_isolated ON user_stats(is_isolated)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_stats_biased ON user_stats(is_biased)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ban_records_user ON ban_records(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ban_records_active ON ban_records(is_active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_archived_toots_user ON archived_toots(user_id, archived_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_archived_toots_toot ON archived_toots(toot_id)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_archived_toots_unique ON archived_toots(user_id, toot_id)")
    print("✓ 인덱스 생성 완료")

    # 기본 시스템 설정 삽입
    print("\n기본 설정 삽입 중...")

    default_configs = [
        ('timezone', 'Asia/Seoul', '타임존'),
        ('check_times', '04:00,16:00', '활동량 체크 시간 (12시간 간격)'),
        ('check_period_hours', '48', '체크 기간'),
        ('min_replies_48h', '20', '최소 답글 수'),
        ('reward_reply_count', '100', '재화 지급 기준 답글 수 (N개)'),
        ('reward_per_replies', '10', 'N개당 지급할 재화량 (M원)'),
        ('last_reward_settlement_time', '2025-01-01 00:00:00', '마지막 재화 정산 시각'),
        ('archive_warning_threshold', '3', '툿 아카이빙 경고 임계값 (N회 이상)'),
        ('admin_account_id', '', '어드민 마스토돈 계정 ID (팔로우 감지용)')
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO system_config (key, value, description) VALUES (?, ?, ?)",
        default_configs
    )
    print("✓ 기본 설정 삽입 완료")

    # 기본 경고 템플릿 삽입
    print("\n기본 경고 템플릿 삽입 중...")

    default_templates = [
        ('활동량 미달 기본', 'activity', '@{username}님, 최근 48시간 답글이 {actual_replies}개로 기준({required_replies}개)에 미달했습니다. 커뮤니티 활동에 관심 부탁드립니다.'),
        ('고립 위험 기본', 'isolation', '@{username}님, 최근 대화 상대가 {unique_partners}명으로 적습니다. 다양한 멤버와 소통해보세요!'),
        ('비활동 기본', 'inactive', '@{username}님, 최근 7일 접속률이 {login_rate}%입니다. 커뮤니티에 관심 가져주세요!'),
        ('편중 경고 기본', 'bias', '@{username}님, @{top_partner}와의 대화가 {ratio}%입니다. 다양한 멤버와 소통해보세요!'),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO warning_templates (name, warning_type, template) VALUES (?, ?, ?)",
        default_templates
    )
    print("✓ 기본 경고 템플릿 삽입 완료")

    # 변경사항 저장
    conn.commit()

    # 테이블 목록 확인
    print("\n생성된 테이블:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count}개 레코드")

    conn.close()
    print(f"\n✅ 데이터베이스 초기화 완료: {db_path}")
    print(f"   WAL 모드: 활성화")
    print(f"   외래키: 활성화")


if __name__ == '__main__':
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else 'economy.db'

    print("=" * 60)
    print("마녀봇 관리 시스템 - 데이터베이스 초기화")
    print("=" * 60)
    print(f"DB 경로: {db_path}\n")

    try:
        init_database(db_path)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)
