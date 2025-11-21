"""
VacationRepository tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
import sqlite3
import pytest
from datetime import date, time, datetime


@pytest.fixture
def vacation_repo(temp_db):
    """Create VacationRepository with initialized database"""
    from init_db import initialize_database
    from admin_web.repositories.vacation_repository import VacationRepository

    # Initialize database
    initialize_database(temp_db)

    # Create repository
    repo = VacationRepository(temp_db)

    yield repo


def test_should_create_vacation(vacation_repo, temp_db):
    """
    Vacation을 생성할 수 있어야 한다

    RED: VacationRepository가 아직 없으므로 실패할 것
    """
    from admin_web.models.vacation import Vacation

    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # When: Vacation 생성
    vacation = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5),
        reason='개인 사정',
        approved=True,
        registered_by='admin'
    )

    created = vacation_repo.create(vacation)

    # Then
    assert created.id is not None
    assert created.user_id == 'user@example.com'
    assert created.start_date == date(2025, 1, 1)
    assert created.end_date == date(2025, 1, 5)
    assert created.reason == '개인 사정'
    assert created.approved is True


def test_should_find_vacation_by_id(vacation_repo, temp_db):
    """
    ID로 Vacation을 조회할 수 있어야 한다
    """
    # Given: Vacation 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    cursor.execute("""
        INSERT INTO vacation (
            user_id, start_date, end_date, reason, approved
        ) VALUES (?, ?, ?, ?, ?)
    """, ('user@example.com', '2025-01-01', '2025-01-05', '휴가', 1))
    vacation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # When: ID로 조회
    vacation = vacation_repo.find_by_id(vacation_id)

    # Then
    assert vacation is not None
    assert vacation.id == vacation_id
    assert vacation.user_id == 'user@example.com'
    assert vacation.start_date == date(2025, 1, 1)
    assert vacation.end_date == date(2025, 1, 5)


def test_should_return_none_when_vacation_not_found(vacation_repo):
    """
    존재하지 않는 Vacation 조회 시 None을 반환해야 한다
    """
    # When: 존재하지 않는 ID로 조회
    vacation = vacation_repo.find_by_id(99999)

    # Then
    assert vacation is None


def test_should_find_vacations_by_user(vacation_repo, temp_db):
    """
    유저의 모든 Vacation을 조회할 수 있어야 한다
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
    vacations = vacation_repo.find_by_user('user@example.com')

    # Then
    assert len(vacations) == 3
    assert all(v.user_id == 'user@example.com' for v in vacations)


def test_should_find_all_vacations(vacation_repo, temp_db):
    """
    모든 Vacation을 조회할 수 있어야 한다
    """
    # Given: 유저와 휴가 생성
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

    # When: 전체 휴가 조회
    vacations = vacation_repo.find_all()

    # Then
    assert len(vacations) == 3


def test_should_find_approved_vacations(vacation_repo, temp_db):
    """
    승인된 휴가만 조회할 수 있어야 한다
    """
    # Given: 승인/미승인 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    # 승인된 휴가 2개
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, approved)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-01-01', '2025-01-05', 1))
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, approved)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-02-01', '2025-02-05', 1))

    # 미승인 휴가 1개
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date, approved)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', '2025-03-01', '2025-03-05', 0))

    conn.commit()
    conn.close()

    # When: 승인된 휴가만 조회
    approved = vacation_repo.find_by_approved(True)

    # Then
    assert len(approved) == 2
    assert all(v.approved is True for v in approved)


def test_should_find_vacations_by_date_range(vacation_repo, temp_db):
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
    vacations = vacation_repo.find_by_date_range(
        date(2025, 1, 1),
        date(2025, 2, 28)
    )

    # Then: 1월, 2월 휴가만 조회되어야 함
    assert len(vacations) == 2


def test_should_count_all_vacations(vacation_repo, temp_db):
    """
    전체 Vacation 수를 계산할 수 있어야 한다
    """
    # Given: 유저와 5개의 휴가 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    for i in range(5):
        cursor.execute("""
            INSERT INTO vacation (user_id, start_date, end_date)
            VALUES (?, ?, ?)
        """, ('user@example.com', f'2025-0{i+1}-01', f'2025-0{i+1}-05'))

    conn.commit()
    conn.close()

    # When: 전체 휴가 수 조회
    count = vacation_repo.count()

    # Then
    assert count == 5


def test_should_get_user_vacation_count(vacation_repo, temp_db):
    """
    특정 유저의 Vacation 수를 조회할 수 있어야 한다
    """
    # Given: 2명의 유저와 각각의 휴가 생성
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

    # user1: 3개 휴가
    for i in range(3):
        cursor.execute("""
            INSERT INTO vacation (user_id, start_date, end_date)
            VALUES (?, ?, ?)
        """, ('user1@example.com', f'2025-0{i+1}-01', f'2025-0{i+1}-05'))

    # user2: 1개 휴가
    cursor.execute("""
        INSERT INTO vacation (user_id, start_date, end_date)
        VALUES (?, ?, ?)
    """, ('user2@example.com', '2025-01-01', '2025-01-05'))

    conn.commit()
    conn.close()

    # When: user1의 휴가 수 조회
    count = vacation_repo.get_user_vacation_count('user1@example.com')

    # Then
    assert count == 3


def test_should_handle_optional_time_fields(vacation_repo, temp_db):
    """
    시간 필드(start_time, end_time)를 선택적으로 처리할 수 있어야 한다
    """
    from admin_web.models.vacation import Vacation

    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # When: 시간 필드 포함하여 생성
    vacation = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        start_time=time(9, 0),
        end_date=date(2025, 1, 5),
        end_time=time(18, 0)
    )

    created = vacation_repo.create(vacation)

    # Then
    assert created.start_time == time(9, 0)
    assert created.end_time == time(18, 0)


def test_should_preserve_created_at_timestamp(vacation_repo, temp_db):
    """
    Vacation 생성 시 created_at이 자동으로 설정되어야 한다
    """
    from admin_web.models.vacation import Vacation

    # Given: 유저 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    conn.commit()
    conn.close()

    # When: Vacation 생성
    vacation = Vacation(
        user_id='user@example.com',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5)
    )

    created = vacation_repo.create(vacation)

    # Then
    assert created.created_at is not None
    assert isinstance(created.created_at, datetime)
