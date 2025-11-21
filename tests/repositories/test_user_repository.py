"""
UserRepository tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
import sqlite3
import pytest
from datetime import datetime


@pytest.fixture
def user_repository(temp_db):
    """Create UserRepository with initialized database"""
    from init_db import initialize_database
    from admin_web.repositories.user_repository import UserRepository

    # Initialize database
    initialize_database(temp_db)

    # Create repository
    repo = UserRepository(temp_db)

    yield repo

    # Cleanup is handled by temp_db fixture


def test_should_find_user_by_id(user_repository, temp_db):
    """
    ID로 유저를 찾을 수 있어야 한다

    RED: UserRepository가 아직 없으므로 실패할 것
    """
    from admin_web.models.user import User

    # Given: 테스트 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, balance, warning_count)
        VALUES (?, ?, ?, ?, ?)
    """, ('user1@example.com', 'user1', 'user', 100, 0))
    conn.commit()
    conn.close()

    # When: ID로 유저 조회
    user = user_repository.find_by_id('user1@example.com')

    # Then
    assert user is not None
    assert isinstance(user, User)
    assert user.mastodon_id == 'user1@example.com'
    assert user.username == 'user1'
    assert user.balance == 100


def test_should_return_none_when_user_not_found(user_repository):
    """
    존재하지 않는 유저 조회 시 None을 반환해야 한다
    """
    # When: 존재하지 않는 ID로 조회
    user = user_repository.find_by_id('nonexistent@example.com')

    # Then
    assert user is None


def test_should_find_all_users(user_repository, temp_db):
    """
    모든 유저를 조회할 수 있어야 한다
    """
    # Given: 3명의 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    for i in range(1, 4):
        cursor.execute("""
            INSERT INTO users (mastodon_id, username, role, balance)
            VALUES (?, ?, ?, ?)
        """, (f'user{i}@example.com', f'user{i}', 'user', i * 100))
    conn.commit()
    conn.close()

    # When: 전체 유저 조회
    users = user_repository.find_all()

    # Then
    assert len(users) == 3
    assert all(user.username.startswith('user') for user in users)


def test_should_filter_users_by_role(user_repository, temp_db):
    """
    역할로 유저를 필터링할 수 있어야 한다
    """
    # Given: admin 1명, user 2명 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('admin@example.com', 'admin', 'admin'))
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user1@example.com', 'user1', 'user'))
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user2@example.com', 'user2', 'user'))
    conn.commit()
    conn.close()

    # When: admin 역할로 필터링
    admins = user_repository.find_by_role('admin')

    # Then
    assert len(admins) == 1
    assert admins[0].role == 'admin'
    assert admins[0].username == 'admin'


def test_should_create_new_user(user_repository):
    """
    새 유저를 생성할 수 있어야 한다
    """
    from admin_web.models.user import User

    # Given: 새 유저 객체
    user = User(
        mastodon_id='newuser@example.com',
        username='newuser',
        role='user',
        balance=0,
        warning_count=0
    )

    # When: 유저 생성
    created_user = user_repository.create(user)

    # Then: 생성 확인
    assert created_user is not None
    assert created_user.mastodon_id == 'newuser@example.com'

    # 조회로 확인
    found_user = user_repository.find_by_id('newuser@example.com')
    assert found_user is not None
    assert found_user.username == 'newuser'


def test_should_raise_error_on_duplicate_user(user_repository, temp_db):
    """
    중복 유저 생성 시 오류가 발생해야 한다
    """
    from admin_web.models.user import User

    # Given: 기존 유저 존재
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('existing@example.com', 'existing', 'user'))
    conn.commit()
    conn.close()

    # When/Then: 중복 생성 시도
    duplicate_user = User(
        mastodon_id='existing@example.com',
        username='duplicate',
        role='user'
    )

    with pytest.raises(sqlite3.IntegrityError):
        user_repository.create(duplicate_user)


def test_should_update_user_balance(user_repository, temp_db):
    """
    유저의 잔액을 업데이트할 수 있어야 한다
    """
    # Given: 초기 잔액 100
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, balance)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 100))
    conn.commit()
    conn.close()

    # When: 잔액 200으로 변경
    user_repository.update_balance('user@example.com', 200)

    # Then: 변경 확인
    user = user_repository.find_by_id('user@example.com')
    assert user.balance == 200


def test_should_increase_balance_and_total_earned(user_repository, temp_db):
    """
    잔액 증가 시 total_earned도 증가해야 한다
    """
    # Given: 초기 잔액 100, total_earned 0
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, balance, total_earned)
        VALUES (?, ?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 100, 0))
    conn.commit()
    conn.close()

    # When: 50 증가
    user_repository.adjust_balance('user@example.com', 50)

    # Then
    user = user_repository.find_by_id('user@example.com')
    assert user.balance == 150
    assert user.total_earned == 50


def test_should_decrease_balance_and_total_spent(user_repository, temp_db):
    """
    잔액 감소 시 total_spent도 증가해야 한다
    """
    # Given: 초기 잔액 100, total_spent 0
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, balance, total_spent)
        VALUES (?, ?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 100, 0))
    conn.commit()
    conn.close()

    # When: 30 감소
    user_repository.adjust_balance('user@example.com', -30)

    # Then
    user = user_repository.find_by_id('user@example.com')
    assert user.balance == 70
    assert user.total_spent == 30


def test_should_not_allow_negative_balance(user_repository, temp_db):
    """
    잔액이 음수가 되는 것을 방지해야 한다
    """
    # Given: 초기 잔액 50
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, balance)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 50))
    conn.commit()
    conn.close()

    # When/Then: 100 감소 시도 (잔액 부족)
    with pytest.raises(ValueError, match='Insufficient balance'):
        user_repository.adjust_balance('user@example.com', -100)


def test_should_update_user_role(user_repository, temp_db):
    """
    유저의 역할을 변경할 수 있어야 한다
    """
    # Given: user 역할
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # When: admin으로 변경
    user_repository.update_role('user@example.com', 'admin')

    # Then
    user = user_repository.find_by_id('user@example.com')
    assert user.role == 'admin'


def test_should_search_users_by_username(user_repository, temp_db):
    """
    유저명으로 검색할 수 있어야 한다
    """
    # Given: 여러 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('alice@example.com', 'alice', 'user'))
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('bob@example.com', 'bob', 'user'))
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('alice2@example.com', 'alice2', 'user'))
    conn.commit()
    conn.close()

    # When: 'alice'로 검색
    results = user_repository.search_by_username('alice')

    # Then: alice와 alice2 모두 포함
    assert len(results) == 2
    assert all('alice' in user.username for user in results)


def test_should_update_warning_count(user_repository, temp_db):
    """
    경고 횟수를 업데이트할 수 있어야 한다
    """
    # Given: 경고 0회
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, warning_count)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 0))
    conn.commit()
    conn.close()

    # When: 경고 1회 증가
    user_repository.increment_warning_count('user@example.com')

    # Then
    user = user_repository.find_by_id('user@example.com')
    assert user.warning_count == 1


def test_should_toggle_key_member_flag(user_repository, temp_db):
    """
    주요 멤버 플래그를 토글할 수 있어야 한다
    """
    # Given: is_key_member = False
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, is_key_member)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 0))
    conn.commit()
    conn.close()

    # When: True로 변경
    user_repository.update_key_member('user@example.com', True)

    # Then
    user = user_repository.find_by_id('user@example.com')
    assert user.is_key_member is True
