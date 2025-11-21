"""
Database initialization tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
import sqlite3
from pathlib import Path


def test_should_create_economy_database(temp_db):
    """
    데이터베이스가 생성되어야 한다
    
    RED: init_db 모듈이 아직 없으므로 실패할 것
    """
    from init_db import initialize_database
    
    # When: 데이터베이스 초기화
    initialize_database(temp_db)
    
    # Then: 데이터베이스 파일이 생성되어야 함
    assert Path(temp_db).exists()
    assert Path(temp_db).stat().st_size > 0


def test_should_create_18_tables(db_connection, temp_db):
    """
    18개의 테이블이 모두 생성되어야 한다
    
    Expected tables:
    1. users
    2. transactions
    3. warnings
    4. settings
    5. vacation
    6. items
    7. inventory
    8. admin_logs
    9. scheduled_posts
    10. attendances
    11. attendance_posts
    12. calendar_events
    13. user_stats
    14. warning_templates
    15. ban_records
    16. archived_toots
    17. story_events
    18. story_posts
    """
    from init_db import initialize_database
    
    # When: 데이터베이스 초기화
    initialize_database(temp_db)
    
    # Then: 18개 테이블이 모두 존재해야 함
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)

    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        'admin_logs',
        'archived_toots',
        'attendance_posts',
        'attendances',
        'ban_records',
        'calendar_events',
        'inventory',
        'items',
        'scheduled_posts',
        'settings',
        'story_events',
        'story_posts',
        'transactions',
        'user_stats',
        'users',
        'vacation',
        'warning_templates',
        'warnings'
    ]
    
    assert tables == expected_tables, f"Expected {expected_tables}, but got {tables}"


def test_users_table_should_have_required_columns(db_connection, temp_db):
    """
    users 테이블이 필수 컬럼을 가져야 한다
    
    새로 추가된 컬럼:
    - warning_count (누적 경고 횟수)
    - is_key_member (주요 멤버 여부, 회피 패턴 감지용)
    """
    from init_db import initialize_database
    
    # When
    initialize_database(temp_db)
    
    # Then
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(users)")
    
    columns = {row[1] for row in cursor.fetchall()}
    
    required_columns = {
        'mastodon_id',
        'username',
        'display_name',
        'role',
        'dormitory',
        'balance',
        'total_earned',
        'total_spent',
        'reply_count',
        'warning_count',  # 새로 추가
        'is_key_member',  # 새로 추가
        'last_active',
        'last_check',
        'created_at'
    }
    
    assert required_columns.issubset(columns), \
        f"Missing columns: {required_columns - columns}"


def test_transactions_table_should_have_category_column(db_connection, temp_db):
    """
    transactions 테이블이 category 컬럼을 가져야 한다
    """
    from init_db import initialize_database
    
    # When
    initialize_database(temp_db)
    
    # Then
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(transactions)")
    
    columns = {row[1] for row in cursor.fetchall()}
    
    assert 'category' in columns, "transactions table should have 'category' column"


def test_items_table_should_have_inventory_management_columns(db_connection, temp_db):
    """
    items 테이블이 재고 관리 컬럼들을 가져야 한다
    """
    from init_db import initialize_database
    
    # When
    initialize_database(temp_db)
    
    # Then
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(items)")
    
    columns = {row[1] for row in cursor.fetchall()}
    
    inventory_columns = {
        'initial_stock',
        'current_stock',
        'sold_count',
        'is_unlimited_stock',
        'max_purchase_per_user',
        'total_sales'
    }
    
    assert inventory_columns.issubset(columns), \
        f"Missing inventory columns: {inventory_columns - columns}"


def test_user_stats_table_should_have_avoidance_columns(db_connection, temp_db):
    """
    user_stats 테이블이 회피 패턴 감지 컬럼들을 가져야 한다
    """
    from init_db import initialize_database
    
    # When
    initialize_database(temp_db)
    
    # Then
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(user_stats)")
    
    columns = {row[1] for row in cursor.fetchall()}
    
    avoidance_columns = {
        'is_avoiding',
        'avoided_users'
    }
    
    assert avoidance_columns.issubset(columns), \
        f"Missing avoidance columns: {avoidance_columns - columns}"
