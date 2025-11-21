"""
Transaction model tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
from datetime import datetime
from dataclasses import asdict
import json


def test_should_create_transaction_with_required_fields():
    """
    필수 필드로 Transaction을 생성할 수 있어야 한다

    RED: Transaction 모델이 아직 없으므로 실패할 것
    """
    from admin_web.models.transaction import Transaction

    # When: 필수 필드로 Transaction 생성
    transaction = Transaction(
        user_id='user@example.com',
        transaction_type='manual_adjust',
        amount=100
    )

    # Then: 필드 값이 올바르게 설정되어야 함
    assert transaction.user_id == 'user@example.com'
    assert transaction.transaction_type == 'manual_adjust'
    assert transaction.amount == 100
    assert transaction.id is None


def test_should_create_transaction_with_optional_fields():
    """
    선택 필드를 포함하여 Transaction을 생성할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # When: 선택 필드 포함
    now = datetime.now()
    transaction = Transaction(
        id=1,
        user_id='user@example.com',
        transaction_type='shop_purchase',
        amount=-50,
        status_id='status123',
        item_id=10,
        category='구매',
        description='아이템 구매',
        admin_name='admin',
        timestamp=now
    )

    # Then
    assert transaction.id == 1
    assert transaction.status_id == 'status123'
    assert transaction.item_id == 10
    assert transaction.category == '구매'
    assert transaction.description == '아이템 구매'
    assert transaction.admin_name == 'admin'
    assert transaction.timestamp == now


def test_should_set_default_values():
    """
    기본값이 올바르게 설정되어야 한다
    """
    from admin_web.models.transaction import Transaction

    # When: 최소 필드로 생성
    transaction = Transaction(
        user_id='user@example.com',
        transaction_type='reward_settlement',
        amount=100
    )

    # Then: 기본값 확인
    assert transaction.id is None
    assert transaction.status_id is None
    assert transaction.item_id is None
    assert transaction.category is None
    assert transaction.description is None
    assert transaction.admin_name is None
    assert transaction.timestamp is None


def test_should_serialize_to_dict():
    """
    Transaction을 딕셔너리로 직렬화할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given
    transaction = Transaction(
        id=1,
        user_id='user@example.com',
        transaction_type='manual_adjust',
        amount=100,
        category='수동조정',
        admin_name='admin'
    )

    # When: 딕셔너리로 변환
    trans_dict = asdict(transaction)

    # Then
    assert trans_dict['id'] == 1
    assert trans_dict['user_id'] == 'user@example.com'
    assert trans_dict['transaction_type'] == 'manual_adjust'
    assert trans_dict['amount'] == 100
    assert trans_dict['category'] == '수동조정'
    assert trans_dict['admin_name'] == 'admin'


def test_should_serialize_to_json():
    """
    Transaction을 JSON으로 직렬화할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given
    transaction = Transaction(
        user_id='user@example.com',
        transaction_type='attendance',
        amount=50,
        category='출석',
        description='출석 보상'
    )

    # When: to_dict() 메서드 호출
    trans_dict = transaction.to_dict()

    # Then: JSON 직렬화 가능해야 함
    json_str = json.dumps(trans_dict)
    assert 'user@example.com' in json_str
    assert 'attendance' in json_str


def test_should_create_transaction_from_dict():
    """
    딕셔너리로부터 Transaction을 생성할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given
    data = {
        'id': 1,
        'user_id': 'user@example.com',
        'transaction_type': 'shop_purchase',
        'amount': -100,
        'category': '구매',
        'description': '상점 구매',
        'item_id': 5
    }

    # When: from_dict() 메서드 호출
    transaction = Transaction.from_dict(data)

    # Then
    assert transaction.id == 1
    assert transaction.user_id == 'user@example.com'
    assert transaction.transaction_type == 'shop_purchase'
    assert transaction.amount == -100
    assert transaction.category == '구매'
    assert transaction.item_id == 5


def test_should_validate_required_fields():
    """
    필수 필드 누락 시 오류가 발생해야 한다
    """
    from admin_web.models.transaction import Transaction
    import pytest

    # When/Then: user_id 누락
    with pytest.raises(TypeError):
        Transaction(transaction_type='manual_adjust', amount=100)

    # When/Then: transaction_type 누락
    with pytest.raises(TypeError):
        Transaction(user_id='user@example.com', amount=100)

    # When/Then: amount 누락
    with pytest.raises(TypeError):
        Transaction(user_id='user@example.com', transaction_type='manual_adjust')


def test_should_identify_positive_transactions():
    """
    양수 거래(입금)를 식별할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 양수 거래
    transaction = Transaction(
        user_id='user@example.com',
        transaction_type='reward_settlement',
        amount=100
    )

    # Then
    assert transaction.is_credit() is True
    assert transaction.is_debit() is False


def test_should_identify_negative_transactions():
    """
    음수 거래(출금)를 식별할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 음수 거래
    transaction = Transaction(
        user_id='user@example.com',
        transaction_type='shop_purchase',
        amount=-50
    )

    # Then
    assert transaction.is_credit() is False
    assert transaction.is_debit() is True


def test_should_handle_zero_amount():
    """
    금액이 0인 거래를 처리할 수 있어야 한다
    """
    from admin_web.models.transaction import Transaction

    # Given: 금액 0
    transaction = Transaction(
        user_id='user@example.com',
        transaction_type='adjustment',
        amount=0
    )

    # Then
    assert transaction.is_credit() is False
    assert transaction.is_debit() is False
