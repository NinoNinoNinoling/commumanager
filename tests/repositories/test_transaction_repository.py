"""
TransactionRepository tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
import sqlite3
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def transaction_repository(temp_db):
    """Create TransactionRepository with initialized database"""
    from init_db import initialize_database
    from admin_web.repositories.transaction_repository import TransactionRepository

    # Initialize database
    initialize_database(temp_db)

    # Create repository
    repo = TransactionRepository(temp_db)

    yield repo


def test_should_create_transaction(transaction_repository, temp_db):
    """
    거래를 생성할 수 있어야 한다

    RED: TransactionRepository가 아직 없으므로 실패할 것
    """
    from admin_web.models.transaction import Transaction

    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # When: 거래 생성
    transaction = Transaction(
        user_id='user@example.com',
        transaction_type='manual_adjust',
        amount=100,
        category='수동조정',
        description='테스트 조정',
        admin_name='admin'
    )

    created = transaction_repository.create(transaction)

    # Then
    assert created is not None
    assert created.id is not None
    assert created.user_id == 'user@example.com'
    assert created.amount == 100
    assert created.category == '수동조정'


def test_should_find_transactions_by_user(transaction_repository, temp_db):
    """
    특정 유저의 거래 내역을 조회할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 유저와 거래 내역 생성
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
    conn.commit()
    conn.close()

    # user1의 거래 2개
    transaction_repository.create(Transaction(
        user_id='user1@example.com',
        transaction_type='reward',
        amount=50
    ))
    transaction_repository.create(Transaction(
        user_id='user1@example.com',
        transaction_type='attendance',
        amount=50
    ))

    # user2의 거래 1개
    transaction_repository.create(Transaction(
        user_id='user2@example.com',
        transaction_type='reward',
        amount=30
    ))

    # When: user1의 거래 조회
    user1_transactions = transaction_repository.find_by_user('user1@example.com')

    # Then
    assert len(user1_transactions) == 2
    assert all(t.user_id == 'user1@example.com' for t in user1_transactions)


def test_should_find_all_transactions(transaction_repository, temp_db):
    """
    모든 거래를 조회할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 유저와 거래 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # 3개 거래 생성
    for i in range(3):
        transaction_repository.create(Transaction(
            user_id='user@example.com',
            transaction_type='reward',
            amount=(i + 1) * 10
        ))

    # When: 전체 거래 조회
    transactions = transaction_repository.find_all()

    # Then
    assert len(transactions) == 3


def test_should_filter_by_type(transaction_repository, temp_db):
    """
    거래 유형으로 필터링할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 유저와 다양한 타입의 거래 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='reward',
        amount=50
    ))
    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='attendance',
        amount=50
    ))
    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='reward',
        amount=30
    ))

    # When: 'reward' 타입으로 필터링
    rewards = transaction_repository.find_by_type('reward')

    # Then
    assert len(rewards) == 2
    assert all(t.transaction_type == 'reward' for t in rewards)


def test_should_filter_by_category(transaction_repository, temp_db):
    """
    카테고리로 필터링할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 유저와 거래 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='manual_adjust',
        amount=100,
        category='수동조정'
    ))
    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='shop_purchase',
        amount=-50,
        category='구매'
    ))
    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='manual_adjust',
        amount=50,
        category='수동조정'
    ))

    # When: '수동조정' 카테고리로 필터링
    manual_adjustments = transaction_repository.find_by_category('수동조정')

    # Then
    assert len(manual_adjustments) == 2
    assert all(t.category == '수동조정' for t in manual_adjustments)


def test_should_count_total_transactions(transaction_repository, temp_db):
    """
    전체 거래 개수를 카운트할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 유저와 거래 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    for i in range(5):
        transaction_repository.create(Transaction(
            user_id='user@example.com',
            transaction_type='reward',
            amount=10
        ))

    # When: 전체 개수 조회
    count = transaction_repository.count()

    # Then
    assert count == 5


def test_should_get_user_transaction_summary(transaction_repository, temp_db):
    """
    유저의 거래 요약(총 입금, 총 출금)을 계산할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 유저와 입출금 거래 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # 입금: +100, +50
    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='reward',
        amount=100
    ))
    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='attendance',
        amount=50
    ))

    # 출금: -30
    transaction_repository.create(Transaction(
        user_id='user@example.com',
        transaction_type='shop_purchase',
        amount=-30
    ))

    # When: 요약 조회
    summary = transaction_repository.get_user_summary('user@example.com')

    # Then
    assert summary['total_credit'] == 150  # 100 + 50
    assert summary['total_debit'] == 30    # |-30|
    assert summary['net_amount'] == 120    # 150 - 30
