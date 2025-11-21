"""
User model tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
from datetime import datetime
from dataclasses import asdict
import json


def test_should_create_user_with_required_fields():
    """
    필수 필드로 User를 생성할 수 있어야 한다

    RED: User 모델이 아직 없으므로 실패할 것
    """
    from admin_web.models.user import User

    # When: 필수 필드로 User 생성
    user = User(
        mastodon_id='user@example.com',
        username='testuser',
        role='user',
        balance=0,
        total_earned=0,
        total_spent=0,
        reply_count=0,
        warning_count=0,
        is_key_member=False
    )

    # Then: 필드 값이 올바르게 설정되어야 함
    assert user.mastodon_id == 'user@example.com'
    assert user.username == 'testuser'
    assert user.role == 'user'
    assert user.balance == 0
    assert user.warning_count == 0
    assert user.is_key_member is False


def test_should_create_user_with_optional_fields():
    """
    선택 필드를 포함하여 User를 생성할 수 있어야 한다
    """
    from admin_web.models.user import User

    # When: 선택 필드 포함
    now = datetime.now()
    user = User(
        mastodon_id='user@example.com',
        username='testuser',
        display_name='Test User',
        role='user',
        dormitory='A동',
        balance=100,
        total_earned=100,
        total_spent=0,
        reply_count=50,
        warning_count=1,
        is_key_member=True,
        last_active=now,
        last_check=now,
        created_at=now
    )

    # Then
    assert user.display_name == 'Test User'
    assert user.dormitory == 'A동'
    assert user.warning_count == 1
    assert user.is_key_member is True
    assert user.last_active == now


def test_should_set_default_values():
    """
    기본값이 올바르게 설정되어야 한다
    """
    from admin_web.models.user import User

    # When: 최소 필드로 생성
    user = User(
        mastodon_id='user@example.com',
        username='testuser'
    )

    # Then: 기본값 확인
    assert user.role == 'user'
    assert user.balance == 0
    assert user.total_earned == 0
    assert user.total_spent == 0
    assert user.reply_count == 0
    assert user.warning_count == 0
    assert user.is_key_member is False
    assert user.display_name is None
    assert user.dormitory is None
    assert user.last_active is None
    assert user.last_check is None
    assert user.created_at is None


def test_should_serialize_to_dict():
    """
    User를 딕셔너리로 직렬화할 수 있어야 한다
    """
    from admin_web.models.user import User

    # Given
    user = User(
        mastodon_id='user@example.com',
        username='testuser',
        role='admin',
        balance=500,
        warning_count=2,
        is_key_member=True
    )

    # When: 딕셔너리로 변환
    user_dict = asdict(user)

    # Then
    assert user_dict['mastodon_id'] == 'user@example.com'
    assert user_dict['username'] == 'testuser'
    assert user_dict['role'] == 'admin'
    assert user_dict['balance'] == 500
    assert user_dict['warning_count'] == 2
    assert user_dict['is_key_member'] is True


def test_should_serialize_to_json():
    """
    User를 JSON으로 직렬화할 수 있어야 한다
    """
    from admin_web.models.user import User

    # Given
    user = User(
        mastodon_id='user@example.com',
        username='testuser',
        balance=100,
        warning_count=0,
        is_key_member=False
    )

    # When: to_dict() 메서드 호출
    user_dict = user.to_dict()

    # Then: JSON 직렬화 가능해야 함
    json_str = json.dumps(user_dict)
    assert 'user@example.com' in json_str
    assert 'testuser' in json_str


def test_should_create_user_from_dict():
    """
    딕셔너리로부터 User를 생성할 수 있어야 한다
    """
    from admin_web.models.user import User

    # Given
    data = {
        'mastodon_id': 'user@example.com',
        'username': 'testuser',
        'display_name': 'Test User',
        'role': 'user',
        'balance': 100,
        'warning_count': 1,
        'is_key_member': True
    }

    # When: from_dict() 메서드 호출
    user = User.from_dict(data)

    # Then
    assert user.mastodon_id == 'user@example.com'
    assert user.username == 'testuser'
    assert user.display_name == 'Test User'
    assert user.warning_count == 1
    assert user.is_key_member is True


def test_should_validate_required_fields():
    """
    필수 필드 누락 시 오류가 발생해야 한다
    """
    from admin_web.models.user import User
    import pytest

    # When/Then: mastodon_id 누락
    with pytest.raises(TypeError):
        User(username='testuser')

    # When/Then: username 누락
    with pytest.raises(TypeError):
        User(mastodon_id='user@example.com')


def test_should_check_if_user_has_warnings():
    """
    User가 경고를 받았는지 확인할 수 있어야 한다
    """
    from admin_web.models.user import User

    # Given: 경고 없는 유저
    user1 = User(
        mastodon_id='user1@example.com',
        username='user1',
        warning_count=0
    )

    # Given: 경고 있는 유저
    user2 = User(
        mastodon_id='user2@example.com',
        username='user2',
        warning_count=2
    )

    # Then
    assert user1.has_warnings() is False
    assert user2.has_warnings() is True


def test_should_check_if_user_is_at_risk_of_ban():
    """
    User가 자동 아웃 위험에 처했는지 확인할 수 있어야 한다

    경고 3회 도달 시 자동 아웃
    """
    from admin_web.models.user import User

    # Given: 경고 2회 유저
    user1 = User(
        mastodon_id='user1@example.com',
        username='user1',
        warning_count=2
    )

    # Given: 경고 3회 유저
    user2 = User(
        mastodon_id='user2@example.com',
        username='user2',
        warning_count=3
    )

    # Then
    assert user1.is_at_risk_of_ban() is True
    assert user2.is_at_risk_of_ban() is False  # 이미 아웃되어야 함
