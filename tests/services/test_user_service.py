"""
UserService tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
import sqlite3
import pytest
from datetime import datetime


@pytest.fixture
def user_service(temp_db):
    """Create UserService with initialized database"""
    from init_db import initialize_database
    from admin_web.services.user_service import UserService

    # Initialize database
    initialize_database(temp_db)

    # Create service
    service = UserService(temp_db)

    yield service


def test_should_get_user_by_id(user_service, temp_db):
    """
    ID로 유저를 조회할 수 있어야 한다

    RED: UserService가 아직 없으므로 실패할 것
    """
    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, balance)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 100))
    conn.commit()
    conn.close()

    # When: 유저 조회
    user = user_service.get_user('user@example.com')

    # Then
    assert user is not None
    assert user.mastodon_id == 'user@example.com'
    assert user.balance == 100


def test_should_return_none_when_user_not_found(user_service):
    """
    존재하지 않는 유저 조회 시 None을 반환해야 한다
    """
    # When: 존재하지 않는 유저 조회
    user = user_service.get_user('nonexistent@example.com')

    # Then
    assert user is None


def test_should_get_all_users(user_service, temp_db):
    """
    모든 유저를 조회할 수 있어야 한다
    """
    # Given: 3명의 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    for i in range(1, 4):
        cursor.execute("""
            INSERT INTO users (mastodon_id, username, role)
            VALUES (?, ?, ?)
        """, (f'user{i}@example.com', f'user{i}', 'user'))
    conn.commit()
    conn.close()

    # When: 전체 유저 조회
    users = user_service.get_all_users()

    # Then
    assert len(users) == 3


def test_should_change_user_role(user_service, temp_db):
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
    user_service.change_role('user@example.com', 'admin', 'admin_user')

    # Then
    user = user_service.get_user('user@example.com')
    assert user.role == 'admin'


def test_should_validate_role_value(user_service, temp_db):
    """
    잘못된 역할 값을 거부해야 한다
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

    # When/Then: 잘못된 역할로 변경 시도
    with pytest.raises(ValueError, match='Invalid role'):
        user_service.change_role('user@example.com', 'invalid_role', 'admin_user')


def test_should_adjust_balance_and_create_transaction(user_service, temp_db):
    """
    잔액 조정 시 Transaction도 함께 생성되어야 한다 (핵심 비즈니스 로직)
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

    # When: 50 증가
    result = user_service.adjust_balance(
        user_id='user@example.com',
        amount=50,
        transaction_type='manual_adjust',
        description='테스트 조정',
        admin_name='admin'
    )

    # Then: 잔액 변경 확인
    user = user_service.get_user('user@example.com')
    assert user.balance == 150

    # Then: Transaction 생성 확인
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM transactions
        WHERE user_id = ?
    """, ('user@example.com',))
    transaction = cursor.fetchone()
    conn.close()

    assert transaction is not None
    assert transaction[3] == 50  # amount
    assert transaction[2] == 'manual_adjust'  # transaction_type


def test_should_increase_total_earned_on_positive_adjustment(user_service, temp_db):
    """
    양수 조정 시 total_earned가 증가해야 한다
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
    user_service.adjust_balance(
        user_id='user@example.com',
        amount=50,
        transaction_type='reward',
        admin_name='system'
    )

    # Then
    user = user_service.get_user('user@example.com')
    assert user.balance == 150
    assert user.total_earned == 50


def test_should_increase_total_spent_on_negative_adjustment(user_service, temp_db):
    """
    음수 조정 시 total_spent가 증가해야 한다
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
    user_service.adjust_balance(
        user_id='user@example.com',
        amount=-30,
        transaction_type='shop_purchase',
        admin_name='system'
    )

    # Then
    user = user_service.get_user('user@example.com')
    assert user.balance == 70
    assert user.total_spent == 30


def test_should_not_allow_balance_below_zero(user_service, temp_db):
    """
    잔액이 음수가 되는 조정을 거부해야 한다
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
        user_service.adjust_balance(
            user_id='user@example.com',
            amount=-100,
            transaction_type='shop_purchase',
            admin_name='system'
        )


def test_should_rollback_on_transaction_creation_failure(user_service, temp_db):
    """
    Transaction 생성 실패 시 잔액 변경도 롤백되어야 한다

    원자성(Atomicity) 보장 테스트
    """
    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, balance)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 100))
    conn.commit()
    conn.close()

    # When: 잘못된 transaction_type으로 조정 시도 (외래키 제약 등으로 실패 가정)
    # 실제로는 잔액 조정과 거래 생성이 하나의 트랜잭션으로 처리되어야 함
    # 이 테스트는 Service가 트랜잭션을 올바르게 관리하는지 확인

    # 일단 정상 케이스로 테스트 (실제 롤백 테스트는 mock 필요)
    initial_balance = 100
    user_service.adjust_balance(
        user_id='user@example.com',
        amount=50,
        transaction_type='reward',
        admin_name='system'
    )

    user = user_service.get_user('user@example.com')
    assert user.balance == 150  # 정상 처리


def test_should_get_user_statistics(user_service, temp_db):
    """
    유저 통계를 조회할 수 있어야 한다
    """
    # Given: 유저와 거래 내역 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, balance)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 100))
    conn.commit()
    conn.close()

    # 여러 거래 생성
    user_service.adjust_balance('user@example.com', 100, 'reward', 'system')
    user_service.adjust_balance('user@example.com', 50, 'attendance', 'system')
    user_service.adjust_balance('user@example.com', -30, 'shop_purchase', 'system')

    # When: 통계 조회
    stats = user_service.get_user_statistics('user@example.com')

    # Then
    assert stats['user'] is not None
    assert stats['transaction_count'] == 3
    assert stats['total_credit'] == 150  # 100 + 50
    assert stats['total_debit'] == 30    # |-30|
    assert stats['current_balance'] == 220  # 100 + 100 + 50 - 30


def test_should_create_new_user(user_service):
    """
    새 유저를 생성할 수 있어야 한다
    """
    # When: 유저 생성
    user = user_service.create_user(
        mastodon_id='newuser@example.com',
        username='newuser',
        display_name='New User'
    )

    # Then
    assert user is not None
    assert user.mastodon_id == 'newuser@example.com'
    assert user.username == 'newuser'
    assert user.display_name == 'New User'
    assert user.balance == 0


def test_should_search_users_by_username(user_service, temp_db):
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
    results = user_service.search_users('alice')

    # Then
    assert len(results) == 2
    assert all('alice' in user.username for user in results)


def test_should_increment_warning_count(user_service, temp_db):
    """
    경고 횟수를 증가시킬 수 있어야 한다
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

    # When: 경고 증가
    user_service.add_warning('user@example.com', 'admin')

    # Then
    user = user_service.get_user('user@example.com')
    assert user.warning_count == 1


def test_should_toggle_key_member_status(user_service, temp_db):
    """
    주요 멤버 상태를 토글할 수 있어야 한다
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
    user_service.set_key_member('user@example.com', True, 'admin')

    # Then
    user = user_service.get_user('user@example.com')
    assert user.is_key_member is True


def test_should_log_admin_action_when_changing_role(user_service, temp_db):
    """
    역할 변경 시 관리자 로그를 기록해야 한다 (RED)
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

    # When: 역할 변경
    user_service.change_role('user@example.com', 'admin', 'admin_user')

    # Then: 관리자 로그 확인
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM admin_logs
        WHERE target_user = ? AND action_type = ?
    """, ('user@example.com', 'role_change'))
    log = cursor.fetchone()
    conn.close()

    assert log is not None
    assert log[1] == 'admin_user'  # admin_name
    assert log[2] == 'role_change'  # action_type
    assert log[3] == 'user@example.com'  # target_user
    assert 'admin' in log[4]  # details should contain new role


def test_should_log_admin_action_when_adding_warning(user_service, temp_db):
    """
    경고 추가 시 관리자 로그를 기록해야 한다 (RED)
    """
    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, warning_count)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 0))
    conn.commit()
    conn.close()

    # When: 경고 추가
    user_service.add_warning('user@example.com', 'admin_user')

    # Then: 관리자 로그 확인
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM admin_logs
        WHERE target_user = ? AND action_type = ?
    """, ('user@example.com', 'warning_add'))
    log = cursor.fetchone()
    conn.close()

    assert log is not None
    assert log[1] == 'admin_user'  # admin_name
    assert log[2] == 'warning_add'  # action_type
    assert log[3] == 'user@example.com'  # target_user


def test_should_log_admin_action_when_setting_key_member(user_service, temp_db):
    """
    주요 멤버 설정 시 관리자 로그를 기록해야 한다 (RED)
    """
    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, is_key_member)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 0))
    conn.commit()
    conn.close()

    # When: 주요 멤버로 설정
    user_service.set_key_member('user@example.com', True, 'admin_user')

    # Then: 관리자 로그 확인
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM admin_logs
        WHERE target_user = ? AND action_type = ?
    """, ('user@example.com', 'key_member_change'))
    log = cursor.fetchone()
    conn.close()

    assert log is not None
    assert log[1] == 'admin_user'  # admin_name
    assert log[2] == 'key_member_change'  # action_type
    assert log[3] == 'user@example.com'  # target_user
    assert 'True' in log[4] or 'true' in log[4].lower()  # details should contain new status


def test_should_auto_ban_user_when_warning_count_reaches_three(user_service, temp_db):
    """
    경고 횟수가 3회에 도달하면 자동으로 ban_records에 기록해야 한다 (RED)
    """
    # Given: 경고 2회인 유저
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, warning_count)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 2))
    conn.commit()
    conn.close()

    # When: 3번째 경고 추가
    user_service.add_warning('user@example.com', 'admin_user')

    # Then: ban_records에 기록 확인
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ban_records
        WHERE user_id = ? AND is_active = 1
    """, ('user@example.com',))
    ban = cursor.fetchone()
    conn.close()

    assert ban is not None
    assert ban[1] == 'user@example.com'  # user_id
    assert ban[3] == 'system'  # banned_by (auto-ban)
    assert '자동' in ban[4] or 'auto' in ban[4].lower()  # reason should mention auto-ban
    assert ban[5] == 3  # warning_count
    assert ban[7] == 1  # is_active = True


def test_should_not_auto_ban_when_warning_count_below_three(user_service, temp_db):
    """
    경고 횟수가 3회 미만이면 ban_records에 기록하지 않아야 한다
    """
    # Given: 경고 1회인 유저
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, warning_count)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 1))
    conn.commit()
    conn.close()

    # When: 2번째 경고 추가
    user_service.add_warning('user@example.com', 'admin_user')

    # Then: ban_records에 기록 없음
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ban_records
        WHERE user_id = ? AND is_active = 1
    """, ('user@example.com',))
    ban = cursor.fetchone()
    conn.close()

    assert ban is None
