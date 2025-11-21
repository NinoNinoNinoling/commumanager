"""
Vacation model tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
from datetime import date, time, datetime
from dataclasses import asdict
import json


def test_should_create_vacation_with_required_fields():
    """
    필수 필드로 Vacation을 생성할 수 있어야 한다

    RED: Vacation 모델이 아직 없으므로 실패할 것
    """
    from admin_web.models.vacation import Vacation

    # When: 필수 필드로 Vacation 생성
    vacation = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5)
    )

    # Then: 필드 값이 올바르게 설정되어야 함
    assert vacation.user_id == 'user@example.com'
    assert vacation.start_date == date(2025, 1, 1)
    assert vacation.end_date == date(2025, 1, 5)
    assert vacation.id is None
    assert vacation.approved is True


def test_should_create_vacation_with_optional_fields():
    """
    선택 필드를 포함하여 Vacation을 생성할 수 있어야 한다
    """
    from admin_web.models.vacation import Vacation

    # When: 선택 필드 포함
    now = datetime.now()
    vacation = Vacation(
        id=1,
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        start_time=time(9, 0),
        end_date=date(2025, 1, 5),
        end_time=time(18, 0),
        reason='개인 사정',
        approved=False,
        registered_by='admin',
        created_at=now
    )

    # Then
    assert vacation.id == 1
    assert vacation.start_time == time(9, 0)
    assert vacation.end_time == time(18, 0)
    assert vacation.reason == '개인 사정'
    assert vacation.approved is False
    assert vacation.registered_by == 'admin'
    assert vacation.created_at == now


def test_should_set_default_values():
    """
    기본값이 올바르게 설정되어야 한다
    """
    from admin_web.models.vacation import Vacation

    # When: 최소 필드로 생성
    vacation = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5)
    )

    # Then: 기본값 확인
    assert vacation.id is None
    assert vacation.start_time is None
    assert vacation.end_time is None
    assert vacation.reason is None
    assert vacation.approved is True
    assert vacation.registered_by is None
    assert vacation.created_at is None


def test_should_serialize_to_dict():
    """
    Vacation을 딕셔너리로 직렬화할 수 있어야 한다
    """
    from admin_web.models.vacation import Vacation

    # Given
    vacation = Vacation(
        id=1,
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5),
        reason='휴가',
        approved=True
    )

    # When: 딕셔너리로 변환
    vacation_dict = asdict(vacation)

    # Then
    assert vacation_dict['id'] == 1
    assert vacation_dict['user_id'] == 'user@example.com'
    assert vacation_dict['start_date'] == date(2025, 1, 1)
    assert vacation_dict['end_date'] == date(2025, 1, 5)
    assert vacation_dict['reason'] == '휴가'
    assert vacation_dict['approved'] is True


def test_should_serialize_to_json():
    """
    Vacation을 JSON으로 직렬화할 수 있어야 한다
    """
    from admin_web.models.vacation import Vacation

    # Given
    vacation = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5)
    )

    # When: to_dict() 메서드 호출
    vacation_dict = vacation.to_dict()

    # Then: JSON 직렬화 가능해야 함
    json_str = json.dumps(vacation_dict)
    assert 'user@example.com' in json_str
    assert '2025-01-01' in json_str


def test_should_create_vacation_from_dict():
    """
    딕셔너리로부터 Vacation을 생성할 수 있어야 한다
    """
    from admin_web.models.vacation import Vacation

    # Given
    data = {
        'id': 1,
        'user_id': 'user@example.com',
        'start_date': '2025-01-01',
        'end_date': '2025-01-05',
        'reason': '휴가',
        'approved': True
    }

    # When: from_dict() 메서드 호출
    vacation = Vacation.from_dict(data)

    # Then
    assert vacation.id == 1
    assert vacation.user_id == 'user@example.com'
    assert vacation.start_date == date(2025, 1, 1)
    assert vacation.end_date == date(2025, 1, 5)
    assert vacation.reason == '휴가'
    assert vacation.approved is True


def test_should_validate_required_fields():
    """
    필수 필드 누락 시 오류가 발생해야 한다
    """
    from admin_web.models.vacation import Vacation
    import pytest

    # When/Then: user_id 누락
    with pytest.raises(TypeError):
        Vacation(start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))

    # When/Then: start_date 누락
    with pytest.raises(TypeError):
        Vacation(user_id='user@example.com', end_date=date(2025, 1, 5))

    # When/Then: end_date 누락
    with pytest.raises(TypeError):
        Vacation(user_id='user@example.com', start_date=date(2025, 1, 1))


def test_should_check_if_approved():
    """
    승인 여부를 확인할 수 있어야 한다
    """
    from admin_web.models.vacation import Vacation

    # Given: 승인된 휴가
    vacation1 = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5),
        approved=True
    )

    # Given: 미승인 휴가
    vacation2 = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5),
        approved=False
    )

    # Then
    assert vacation1.is_approved() is True
    assert vacation2.is_approved() is False


def test_should_calculate_duration_days():
    """
    휴가 기간(일수)을 계산할 수 있어야 한다
    """
    from admin_web.models.vacation import Vacation

    # Given: 5일 휴가 (1일~5일 = 5일간)
    vacation = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5)
    )

    # Then: 종료일 - 시작일 + 1
    assert vacation.get_duration_days() == 5


def test_should_calculate_single_day_vacation():
    """
    당일 휴가도 1일로 계산되어야 한다
    """
    from admin_web.models.vacation import Vacation

    # Given: 당일 휴가
    vacation = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 1)
    )

    # Then
    assert vacation.get_duration_days() == 1
