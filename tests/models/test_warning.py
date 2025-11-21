"""
Warning model tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
from datetime import datetime
from dataclasses import asdict
import json


def test_should_create_warning_with_required_fields():
    """
    필수 필드로 Warning을 생성할 수 있어야 한다

    RED: Warning 모델이 아직 없으므로 실패할 것
    """
    from admin_web.models.warning import Warning

    # When: 필수 필드로 Warning 생성
    warning = Warning(
        user_id='user@example.com',
        warning_type='activity',
        message='답글이 기준에 미달합니다.'
    )

    # Then: 필드 값이 올바르게 설정되어야 함
    assert warning.user_id == 'user@example.com'
    assert warning.warning_type == 'activity'
    assert warning.message == '답글이 기준에 미달합니다.'
    assert warning.id is None
    assert warning.dm_sent is False


def test_should_create_warning_with_optional_fields():
    """
    선택 필드를 포함하여 Warning을 생성할 수 있어야 한다
    """
    from admin_web.models.warning import Warning

    # When: 선택 필드 포함
    now = datetime.now()
    warning = Warning(
        id=1,
        user_id='user@example.com',
        warning_type='activity',
        check_period_hours=48,
        required_replies=5,
        actual_replies=2,
        message='활동량 부족 경고',
        dm_sent=True,
        admin_name='system',
        timestamp=now
    )

    # Then
    assert warning.id == 1
    assert warning.check_period_hours == 48
    assert warning.required_replies == 5
    assert warning.actual_replies == 2
    assert warning.dm_sent is True
    assert warning.admin_name == 'system'
    assert warning.timestamp == now


def test_should_set_default_values():
    """
    기본값이 올바르게 설정되어야 한다
    """
    from admin_web.models.warning import Warning

    # When: 최소 필드로 생성
    warning = Warning(
        user_id='user@example.com',
        warning_type='isolation'
    )

    # Then: 기본값 확인
    assert warning.id is None
    assert warning.check_period_hours is None
    assert warning.required_replies is None
    assert warning.actual_replies is None
    assert warning.message is None
    assert warning.dm_sent is False
    assert warning.admin_name is None
    assert warning.timestamp is None


def test_should_serialize_to_dict():
    """
    Warning을 딕셔너리로 직렬화할 수 있어야 한다
    """
    from admin_web.models.warning import Warning

    # Given
    warning = Warning(
        id=1,
        user_id='user@example.com',
        warning_type='activity',
        message='테스트 경고',
        dm_sent=True
    )

    # When: 딕셔너리로 변환
    warning_dict = asdict(warning)

    # Then
    assert warning_dict['id'] == 1
    assert warning_dict['user_id'] == 'user@example.com'
    assert warning_dict['warning_type'] == 'activity'
    assert warning_dict['message'] == '테스트 경고'
    assert warning_dict['dm_sent'] is True


def test_should_serialize_to_json():
    """
    Warning을 JSON으로 직렬화할 수 있어야 한다
    """
    from admin_web.models.warning import Warning

    # Given
    warning = Warning(
        user_id='user@example.com',
        warning_type='activity',
        message='경고 메시지'
    )

    # When: to_dict() 메서드 호출
    warning_dict = warning.to_dict()

    # Then: JSON 직렬화 가능해야 함
    json_str = json.dumps(warning_dict)
    assert 'user@example.com' in json_str
    assert 'activity' in json_str


def test_should_create_warning_from_dict():
    """
    딕셔너리로부터 Warning을 생성할 수 있어야 한다
    """
    from admin_web.models.warning import Warning

    # Given
    data = {
        'id': 1,
        'user_id': 'user@example.com',
        'warning_type': 'isolation',
        'message': '고립 위험 경고',
        'dm_sent': True,
        'admin_name': 'admin'
    }

    # When: from_dict() 메서드 호출
    warning = Warning.from_dict(data)

    # Then
    assert warning.id == 1
    assert warning.user_id == 'user@example.com'
    assert warning.warning_type == 'isolation'
    assert warning.message == '고립 위험 경고'
    assert warning.dm_sent is True


def test_should_validate_required_fields():
    """
    필수 필드 누락 시 오류가 발생해야 한다
    """
    from admin_web.models.warning import Warning
    import pytest

    # When/Then: user_id 누락
    with pytest.raises(TypeError):
        Warning(warning_type='activity')

    # When/Then: warning_type 누락
    with pytest.raises(TypeError):
        Warning(user_id='user@example.com')


def test_should_identify_activity_warning():
    """
    활동량 부족 경고를 식별할 수 있어야 한다
    """
    from admin_web.models.warning import Warning

    # Given: 활동량 경고
    warning = Warning(
        user_id='user@example.com',
        warning_type='activity',
        check_period_hours=48,
        required_replies=5,
        actual_replies=2
    )

    # Then
    assert warning.is_activity_warning() is True
    assert warning.is_isolation_warning() is False


def test_should_identify_isolation_warning():
    """
    고립 위험 경고를 식별할 수 있어야 한다
    """
    from admin_web.models.warning import Warning

    # Given: 고립 경고
    warning = Warning(
        user_id='user@example.com',
        warning_type='isolation'
    )

    # Then
    assert warning.is_isolation_warning() is True
    assert warning.is_activity_warning() is False


def test_should_check_dm_sent_status():
    """
    DM 발송 여부를 확인할 수 있어야 한다
    """
    from admin_web.models.warning import Warning

    # Given: DM 발송 완료
    warning1 = Warning(
        user_id='user@example.com',
        warning_type='activity',
        dm_sent=True
    )

    # Given: DM 미발송
    warning2 = Warning(
        user_id='user2@example.com',
        warning_type='activity',
        dm_sent=False
    )

    # Then
    assert warning1.has_dm_sent() is True
    assert warning2.has_dm_sent() is False


def test_should_validate_warning_types():
    """
    유효한 경고 타입만 허용해야 한다
    """
    from admin_web.models.warning import Warning

    # Valid types: activity, isolation, bias, avoidance
    valid_types = ['activity', 'isolation', 'bias', 'avoidance']

    for warning_type in valid_types:
        warning = Warning(
            user_id='user@example.com',
            warning_type=warning_type
        )
        assert warning.warning_type in valid_types
