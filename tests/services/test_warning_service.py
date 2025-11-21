"""
WarningService tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
import sqlite3
import pytest
from datetime import datetime


@pytest.fixture
def warning_service(temp_db):
    """Create WarningService with initialized database"""
    from init_db import initialize_database
    from admin_web.services.warning_service import WarningService

    # Initialize database
    initialize_database(temp_db)

    # Create service
    service = WarningService(temp_db)

    yield service


def test_should_issue_warning_and_increment_count(warning_service, temp_db):
    """
    경고를 발행하면 Warning 생성과 동시에 유저 warning_count가 증가해야 한다

    RED: WarningService가 아직 없으므로 실패할 것
    """
    # Given: 유저 생성 (warning_count = 0)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, warning_count)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 0))
    conn.commit()
    conn.close()

    # When: 활동량 경고 발행
    result = warning_service.issue_warning(
        user_id='user@example.com',
        warning_type='activity',
        check_period_hours=48,
        required_replies=5,
        actual_replies=2,
        message='활동량 부족 경고',
        admin_name='system'
    )

    # Then: Warning 생성됨
    assert result['warning'] is not None
    assert result['warning'].user_id == 'user@example.com'
    assert result['warning'].warning_type == 'activity'

    # Then: User의 warning_count 증가됨
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT warning_count FROM users WHERE mastodon_id = ?", ('user@example.com',))
    warning_count = cursor.fetchone()[0]
    conn.close()

    assert warning_count == 1


def test_should_get_warning_by_id(warning_service, temp_db):
    """
    ID로 경고를 조회할 수 있어야 한다
    """
    # Given: 유저와 경고 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'activity', '경고'))
    warning_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # When: ID로 조회
    warning = warning_service.get_warning(warning_id)

    # Then
    assert warning is not None
    assert warning.id == warning_id
    assert warning.user_id == 'user@example.com'


def test_should_return_none_when_warning_not_found(warning_service):
    """
    존재하지 않는 경고 조회 시 None을 반환해야 한다
    """
    # When: 존재하지 않는 ID로 조회
    warning = warning_service.get_warning(99999)

    # Then
    assert warning is None


def test_should_get_user_warnings(warning_service, temp_db):
    """
    유저의 모든 경고를 조회할 수 있어야 한다
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
    warnings = warning_service.get_user_warnings('user@example.com')

    # Then
    assert len(warnings) == 3
    assert all(w.user_id == 'user@example.com' for w in warnings)


def test_should_get_warnings_by_type(warning_service, temp_db):
    """
    유형별로 경고를 조회할 수 있어야 한다
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

    conn.commit()
    conn.close()

    # When: 'activity' 유형 조회
    activity_warnings = warning_service.get_warnings_by_type('activity')

    # Then
    assert len(activity_warnings) == 1
    assert activity_warnings[0].warning_type == 'activity'


def test_should_update_dm_sent_status(warning_service, temp_db):
    """
    DM 전송 상태를 업데이트할 수 있어야 한다
    """
    # Given: 유저와 경고 생성 (dm_sent = False)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))
    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message, dm_sent)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'activity', '경고', 0))
    warning_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # When: DM 전송 상태 업데이트
    warning_service.update_dm_sent(warning_id, True)

    # Then
    warning = warning_service.get_warning(warning_id)
    assert warning.dm_sent is True


def test_should_get_warning_statistics(warning_service, temp_db):
    """
    경고 통계를 조회할 수 있어야 한다
    """
    # Given: 유저와 여러 경고 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, warning_count)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 3))

    # 3개 경고 생성 (activity 2개, isolation 1개)
    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'activity', '경고 1'))
    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'activity', '경고 2'))
    cursor.execute("""
        INSERT INTO warnings (user_id, warning_type, message)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'isolation', '경고 3'))

    conn.commit()
    conn.close()

    # When: 통계 조회
    stats = warning_service.get_user_warning_statistics('user@example.com')

    # Then
    assert stats['total_warnings'] == 3
    assert stats['warning_count'] == 3  # User의 warning_count
    assert stats['by_type']['activity'] == 2
    assert stats['by_type']['isolation'] == 1


def test_should_check_if_user_at_risk_of_ban(warning_service, temp_db):
    """
    유저가 자동 아웃 위험에 처했는지 확인할 수 있어야 한다
    """
    # Given: warning_count = 2인 유저
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, warning_count)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 2))
    conn.commit()
    conn.close()

    # When: 위험 여부 확인
    is_at_risk = warning_service.is_user_at_risk_of_ban('user@example.com')

    # Then: 2회 경고면 위험 상태 (3회 도달 시 자동 아웃)
    assert is_at_risk is True


def test_should_not_be_at_risk_with_less_than_2_warnings(warning_service, temp_db):
    """
    경고 2회 미만이면 자동 아웃 위험이 아니어야 한다
    """
    # Given: warning_count = 1인 유저
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role, warning_count)
        VALUES (?, ?, ?, ?)
    """, ('user@example.com', 'user', 'user', 1))
    conn.commit()
    conn.close()

    # When: 위험 여부 확인
    is_at_risk = warning_service.is_user_at_risk_of_ban('user@example.com')

    # Then
    assert is_at_risk is False


def test_should_validate_warning_type(warning_service, temp_db):
    """
    잘못된 경고 유형을 거부해야 한다
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

    # When/Then: 잘못된 유형으로 경고 발행 시도
    with pytest.raises(ValueError, match='Invalid warning type'):
        warning_service.issue_warning(
            user_id='user@example.com',
            warning_type='invalid_type',
            message='경고',
            admin_name='admin'
        )


def test_should_count_warnings_by_type(warning_service, temp_db):
    """
    유형별 경고 수를 계산할 수 있어야 한다
    """
    # Given: 다양한 유형의 경고 생성
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (mastodon_id, username, role)
        VALUES (?, ?, ?)
    """, ('user@example.com', 'user', 'user'))

    # activity 3개
    for i in range(3):
        cursor.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES (?, ?, ?)
        """, ('user@example.com', 'activity', f'경고 {i+1}'))

    # isolation 2개
    for i in range(2):
        cursor.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES (?, ?, ?)
        """, ('user@example.com', 'isolation', f'고립 {i+1}'))

    conn.commit()
    conn.close()

    # When: 유형별 카운트 조회
    counts = warning_service.get_warning_counts_by_type()

    # Then
    assert counts['activity'] == 3
    assert counts['isolation'] == 2
