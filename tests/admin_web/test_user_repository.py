import sqlite3
import pytest
from datetime import datetime
from admin_web.repositories.user_repository import UserRepository

@pytest.fixture
def user_repository(temp_db):
    """데이터베이스 초기화 및 리포지토리 생성"""
    # 테이블 생성 (테스트용 스키마)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            mastodon_id TEXT PRIMARY KEY,
            username TEXT,
            display_name TEXT,
            role TEXT,
            role_name TEXT,
            dormitory TEXT,
            balance INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0,
            total_spent INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            warning_count INTEGER DEFAULT 0,
            is_key_member BOOLEAN DEFAULT 0,
            last_active TIMESTAMP,
            last_check TIMESTAMP,
            created_at TIMESTAMP,
            role_color TEXT
        )
    """)
    conn.commit()
    conn.close()
    
    return UserRepository(temp_db)

def test_find_all_non_system_users(user_repository, temp_db):
    """시스템 유저를 제외한 모든 유저를 조회할 수 있어야 한다."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # 테스트 데이터 삽입
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, display_name, role_name, created_at)
        VALUES 
        ('user1@example.com', 'user1', 'User One', NULL, CURRENT_TIMESTAMP),
        ('user2@example.com', 'user2', 'User Two', 'user', CURRENT_TIMESTAMP),
        ('admin@example.com', 'admin', 'Admin', 'Admin', CURRENT_TIMESTAMP),
        ('bot@example.com', 'bot', 'Bot', 'bot', CURRENT_TIMESTAMP)
    """)
    conn.commit()
    conn.close()

    # When: 시스템 역할 목록 정의 및 조회
    system_roles = ['bot', 'Admin']
    non_system_users = user_repository.find_all_non_system_users(system_roles)

    # Then
    assert len(non_system_users) == 2
    usernames = {u.username for u in non_system_users}
    assert 'user1' in usernames
    assert 'user2' in usernames
    assert 'bot' not in usernames
    assert 'admin' not in usernames
