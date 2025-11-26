"""
StoryEventService tests
"""
import sqlite3
import pytest
from datetime import datetime, timedelta

@pytest.fixture
def story_event_service(temp_db):
    """Create StoryEventService with initialized database"""
    from init_db import initialize_database
    from admin_web.services.story_event_service import StoryEventService

    initialize_database(temp_db)
    # Ensure a user exists to create the event
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (mastodon_id, username, role) VALUES (?, ?, ?)", 
                   ('test_admin_id', 'test_admin', 'admin'))
    conn.commit()
    conn.close()

    return StoryEventService(temp_db)

def test_should_create_story_event(story_event_service, temp_db):
    """
    StoryEventService의 create_event() 메서드는 새 스토리 이벤트를 생성해야 한다.
    """
    # Given
    title = "새로운 스토리 이벤트"
    start_time = datetime(2025, 1, 1, 10, 0, 0)
    created_by = "test_admin"
    interval_minutes = 15

    # When
    result = story_event_service.create_event(title, start_time, created_by, interval_minutes)

    # Then
    assert 'event' in result
    event = result['event']
    assert event.id is not None
    assert event.title == title
    assert event.start_time == start_time
    assert event.created_by == created_by
    assert event.interval_minutes == interval_minutes
    assert event.status == "pending"

    # Verify directly from DB
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row # Add this line
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM story_events WHERE id = ?", (event.id,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row['title'] == title
    assert datetime.fromisoformat(row['start_time']) == start_time
    assert row['created_by'] == created_by
    assert row['interval_minutes'] == interval_minutes
    assert row['status'] == "pending"


def test_should_add_posts_to_story_event(story_event_service, temp_db):
    """
    StoryEventService의 add_posts() 메서드는 스토리 이벤트에 여러 포스트를 추가해야 한다.
    """
    # Given: 스토리 이벤트 생성
    event_title = "포스트 추가 테스트"
    event_start_time = datetime(2025, 1, 1, 12, 0, 0)
    event_created_by = "test_admin"
    created_event_result = story_event_service.create_event(event_title, event_start_time, event_created_by)
    event_id = created_event_result['event'].id

    posts_content = [
        "첫 번째 포스트 내용입니다.",
        "두 번째 포스트 내용입니다.",
        "세 번째 포스트 내용입니다."
    ]

    # When: 포스트들 추가
    result = story_event_service.add_posts(event_id, posts_content)

    # Then
    assert 'posts' in result
    assert result['count'] == len(posts_content)
    assert len(result['posts']) == len(posts_content)

    # Verify directly from DB
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM story_posts WHERE event_id = ? ORDER BY sequence", (event_id,))
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == len(posts_content)
    for i, row in enumerate(rows):
        assert row['content'] == posts_content[i]
        assert row['sequence'] == i + 1
        assert row['event_id'] == event_id


