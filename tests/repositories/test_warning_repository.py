"""
WarningRepository tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
import sqlite3
import pytest
from datetime import datetime

from admin_web.models.warning import Warning


@pytest.fixture
def warning_repo(temp_db):
    """Create WarningRepository with initialized database"""
    from init_db import initialize_database
    from admin_web.repositories.warning_repository import WarningRepository

    # Initialize database
    initialize_database(temp_db)

    # Create repository
    repo = WarningRepository(temp_db)

    yield repo


def test_should_create_warning(warning_repo, temp_db):
    """
    Warning을 생성할 수 있어야 한다

    RED: WarningRepository가 아직 없으므로 실패할 것
    """
    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # When: Warning 생성
    warning = Warning(
        user_id='user@example.com',
        warning_type='activity',
        check_period_hours=48,
        required_replies=5,
        actual_replies=2,
        message='활동량 부족 경고',
        dm_sent=True,
        admin_name='system'
    )

    created = warning_repo.create(warning)

    # Then
    assert created.id is not None
    assert created.user_id == 'user@example.com'
    assert created.warning_type == 'activity'
    assert created.check_period_hours == 48
    assert created.dm_sent is True


def test_should_find_warning_by_id(warning_repo, temp_db):
    """
    ID로 Warning을 조회할 수 있어야 한다
    """
    # Given: Warning 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    cursor.execute("""
        INSERT INTO warnings (
            user_id, warning_type, message, dm_sent, admin_name
        ) VALUES (?, ?, ?, ?, ?)
    """, ('user@example.com', 'activity', '경고 메시지', 1, 'admin'))
    warning_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # When: ID로 조회
    warning = warning_repo.find_by_id(warning_id)

    # Then
    assert warning is not None
    assert warning.id == warning_id
    assert warning.user_id == 'user@example.com'
    assert warning.warning_type == 'activity'


def test_should_return_none_when_warning_not_found(warning_repo):
    """
    존재하지 않는 Warning 조회 시 None을 반환해야 한다
    """
    # When: 존재하지 않는 ID로 조회
    warning = warning_repo.find_by_id(99999)

    # Then
    assert warning is None


def test_should_find_warnings_by_user(warning_repo, temp_db):
    """
    유저의 모든 Warning을 조회할 수 있어야 한다
    """
    # Given: 유저와 3개의 경고 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    for i in range(3):
        cursor.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES (?, ?, ?)
        """, ('user@example.com', 'activity', f'경고 {i+1}'))

    conn.commit()
    conn.close()

    # When: 유저의 경고 조회
    warnings = warning_repo.find_by_user('user@example.com')

    # Then
    assert len(warnings) == 3
    assert all(w.user_id == 'user@example.com' for w in warnings)


def test_should_find_warnings_by_type(warning_repo, temp_db):
    """
    유형별로 Warning을 조회할 수 있어야 한다
    """
    # Given: 유저와 다양한 유형의 경고 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'activity', '활동량 경고'))
    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'isolation', '고립 경고'))
    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'activity', '또 다른 활동량 경고'))

    conn.commit()
    conn.close()

    # When: 'activity' 유형 조회
    activity_warnings = warning_repo.find_by_type('activity')

    # Then
    assert len(activity_warnings) == 2
    assert all(w.warning_type == 'activity' for w in activity_warnings)


def test_should_count_all_warnings(warning_repo, temp_db):
    """
    전체 Warning 수를 계산할 수 있어야 한다
    """
    # Given: 유저와 5개의 경고 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    for i in range(5):
        cursor.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES (?, ?, ?)
        """, ('user@example.com', 'activity', f'경고 {i+1}'))

    conn.commit()
    conn.close()

    # When: 전체 경고 수 조회
    count = warning_repo.count()

    # Then
    assert count == 5


def test_should_get_user_warning_count(warning_repo, temp_db):
    """
    특정 유저의 Warning 수를 조회할 수 있어야 한다
    """
    # Given: 2명의 유저와 각각의 경고 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user1@example.com', 'user1', 'user'))
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user2@example.com', 'user2', 'user'))

    # user1: 3개 경고
    for i in range(3):
        cursor.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES (?, ?, ?)
        """, ('user1@example.com', 'activity', f'경고 {i+1}'))

    # user2: 1개 경고
    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message)
        VALUES (?, ?, ?)
    """, ('user2@example.com', 'activity', '경고'))

    conn.commit()
    conn.close()

    # When: user1의 경고 수 조회
    count = warning_repo.get_user_warning_count('user1@example.com')

    # Then
    assert count == 3


def test_should_find_all_warnings(warning_repo, temp_db):
    """
    모든 Warning을 조회할 수 있어야 한다
    """
    # Given: 유저와 경고 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    for i in range(3):
        cursor.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES (?, ?, ?)
        """, ('user@example.com', 'activity', f'경고 {i+1}'))

    conn.commit()
    conn.close()

    # When: 전체 경고 조회
    warnings = warning_repo.find_all()

    # Then
    assert len(warnings) == 3


def test_should_handle_optional_fields(warning_repo, temp_db):
    """
    선택 필드가 없는 Warning도 생성 가능해야 한다
    """
    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # When: 최소 필드로 Warning 생성
    warning = Warning(
        user_id='user@example.com',
        warning_type='isolation'
    )

    created = warning_repo.create(warning)

    # Then
    assert created.id is not None
    assert created.check_period_hours is None
    assert created.message is None
    assert created.dm_sent is False


def test_should_preserve_timestamp(warning_repo, temp_db):
    """
    Warning 생성 시 timestamp가 자동으로 설정되어야 한다
    """
    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # When: Warning 생성
    warning = Warning(
        user_id='user@example.com',
        warning_type='activity'
    )

    created = warning_repo.create(warning)

    # Then
    assert created.timestamp is not None
    assert isinstance(created.timestamp, datetime)
