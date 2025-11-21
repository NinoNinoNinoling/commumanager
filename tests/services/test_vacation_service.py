"""
VacationService tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
import sqlite3
import pytest
from datetime import date, time, datetime


@pytest.fixture
def vacation_service(temp_db):
    """Create VacationService with initialized database"""
    from init_db import initialize_database
    from admin_web.services.vacation_service import VacationService

    # Initialize database
    initialize_database(temp_db)

    # Create service
    service = VacationService(temp_db)

    yield service


def test_should_create_vacation(vacation_service, temp_db):
    """
    휴가를 생성할 수 있어야 한다

    RED: VacationService가 아직 없으므로 실패할 것
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

    # When: 휴가 생성
    result = vacation_service.create_vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5),
        reason='개인 사정',
        registered_by='admin'
    )

    # Then
    assert result['vacation'] is not None
    assert result['vacation'].user_id == 'user@example.com'
    assert result['vacation'].start_date == date(2025, 1, 1)
    assert result['vacation'].end_date == date(2025, 1, 5)
    assert result['vacation'].reason == '개인 사정'
    assert result['vacation'].approved is True


def test_should_get_vacation_by_id(vacation_service, temp_db):
    """
    ID로 휴가를 조회할 수 있어야 한다
    """
    # Given: 유저와 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, reason)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-01-01', '2025-01-05', '휴가'))
    vacation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # When: ID로 조회
    vacation = vacation_service.get_vacation(vacation_id)

    # Then
    assert vacation is not None
    assert vacation.id == vacation_id
    assert vacation.user_id == 'user@example.com'


def test_should_return_none_when_vacation_not_found(vacation_service):
    """
    존재하지 않는 휴가 조회 시 None을 반환해야 한다
    """
    # When: 존재하지 않는 ID로 조회
    vacation = vacation_service.get_vacation(99999)

    # Then
    assert vacation is None


def test_should_get_user_vacations(vacation_service, temp_db):
    """
    유저의 모든 휴가를 조회할 수 있어야 한다
    """
    # Given: 유저와 3개의 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    for i in range(3):
        cursor.execute("""
            INSERT INTO vacation (user_id, start_date, end_date)
            VALUES (?, ?, ?)
        """, ('user@example.com', f'2025-0{i+1}-01', f'2025-0{i+1}-05'))

    conn.commit()
    conn.close()

    # When: 유저의 휴가 조회
    vacations = vacation_service.get_user_vacations('user@example.com')

    # Then
    assert len(vacations) == 3
    assert all(v.user_id == 'user@example.com' for v in vacations)


def test_should_approve_vacation(vacation_service, temp_db):
    """
    휴가를 승인할 수 있어야 한다
    """
    # Given: 미승인 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, approved)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-01-01', '2025-01-05', 0))
    vacation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # When: 휴가 승인
    result = vacation_service.approve_vacation(vacation_id, 'admin')

    # Then
    assert result is not None
    assert result.approved is True


def test_should_reject_vacation(vacation_service, temp_db):
    """
    휴가를 거부할 수 있어야 한다
    """
    # Given: 승인된 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, approved)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-01-01', '2025-01-05', 1))
    vacation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # When: 휴가 거부
    result = vacation_service.reject_vacation(vacation_id, 'admin')

    # Then
    assert result is not None
    assert result.approved is False


def test_should_get_vacations_by_date_range(vacation_service, temp_db):
    """
    날짜 범위로 휴가를 조회할 수 있어야 한다
    """
    # Given: 다양한 날짜의 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    # 1월 휴가
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date)
        VALUES (?, ?, ?)
    """, ('user@example.com', '2025-01-01', '2025-01-05'))

    # 2월 휴가
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date)
        VALUES (?, ?, ?)
    """, ('user@example.com', '2025-02-01', '2025-02-05'))

    # 3월 휴가
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date)
        VALUES (?, ?, ?)
    """, ('user@example.com', '2025-03-01', '2025-03-05'))

    conn.commit()
    conn.close()

    # When: 1월 1일 ~ 2월 28일 범위 조회
    vacations = vacation_service.get_vacations_by_date_range(
        date(2025, 1, 1),
        date(2025, 2, 28)
    )

    # Then: 1월, 2월 휴가만 조회되어야 함
    assert len(vacations) == 2


def test_should_get_vacation_statistics(vacation_service, temp_db):
    """
    유저의 휴가 통계를 조회할 수 있어야 한다
    """
    # Given: 유저와 여러 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    # 승인된 휴가 2개 (총 10일)
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, approved)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-01-01', '2025-01-05', 1))  # 5일
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, approved)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-02-01', '2025-02-05', 1))  # 5일

    # 미승인 휴가 1개
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, approved)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-03-01', '2025-03-05', 0))

    conn.commit()
    conn.close()

    # When: 통계 조회
    stats = vacation_service.get_user_vacation_statistics('user@example.com')

    # Then
    assert stats['total_vacations'] == 3
    assert stats['approved_vacations'] == 2
    assert stats['pending_vacations'] == 1
    assert stats['total_days'] == 15  # 5 + 5 + 5


def test_should_create_vacation_with_optional_time(vacation_service, temp_db):
    """
    시간 필드를 포함한 휴가를 생성할 수 있어야 한다
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

    # When: 시간 포함 휴가 생성
    result = vacation_service.create_vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        start_time=time(9, 0),
        end_date=date(2025, 1, 5),
        end_time=time(18, 0),
        registered_by='admin'
    )

    # Then
    assert result['vacation'].start_time == time(9, 0)
    assert result['vacation'].end_time == time(18, 0)


def test_should_delete_vacation(vacation_service, temp_db):
    """
    휴가를 삭제할 수 있어야 한다
    """
    # Given: 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date)
        VALUES (?, ?, ?)
    """, ('user@example.com', '2025-01-01', '2025-01-05'))
    vacation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # When: 휴가 삭제
    deleted = vacation_service.delete_vacation(vacation_id, 'admin')

    # Then
    assert deleted is True
    assert vacation_service.get_vacation(vacation_id) is None


def test_should_return_false_when_deleting_nonexistent_vacation(vacation_service):
    """
    존재하지 않는 휴가 삭제 시 False를 반환해야 한다
    """
    # When: 존재하지 않는 휴가 삭제
    deleted = vacation_service.delete_vacation(99999, 'admin')

    # Then
    assert deleted is False
