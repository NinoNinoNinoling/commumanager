"""
ScheduledAnnouncementService tests
"""
import sqlite3
import pytest
from datetime import datetime
from admin_web.models.scheduled_announcement import ScheduledAnnouncement
from admin_web.services.scheduled_announcement_service import ScheduledAnnouncementService
from init_db import initialize_database # Assuming init_db is available to set up tables

@pytest.fixture
def scheduled_announcement_service(temp_db):
    """Create ScheduledAnnouncementService with initialized database"""
    initialize_database(temp_db)
    # Ensure a user exists to create the announcement
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (mastodon_id, username, role) VALUES (?, ?, ?)", 
                   ('test_admin_id', 'test_admin', 'admin'))
    conn.commit()
    conn.close()

    return ScheduledAnnouncementService(temp_db)


def test_should_create_announcement(scheduled_announcement_service, temp_db):
    """
    ScheduledAnnouncementService의 create_announcement() 메서드는 새 예약 공지를 생성해야 한다.
    """
    # Given
    post_type = "announcement"
    content = "시스템 점검 안내입니다."
    scheduled_at = datetime(2025, 1, 1, 10, 0, 0)
    created_by = "test_admin"

    # When
    result = scheduled_announcement_service.create_announcement(post_type, content, scheduled_at, created_by)

    # Then
    assert 'announcement' in result
    announcement = result['announcement']
    assert announcement.id is not None
    assert announcement.post_type == post_type
    assert announcement.content == content
    assert announcement.scheduled_at == scheduled_at
    assert announcement.created_by == created_by
    assert announcement.status == "pending" # Default status

    # Verify directly from DB
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scheduled_posts WHERE id = ?", (announcement.id,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row['post_type'] == post_type
    assert row['content'] == content
    assert datetime.fromisoformat(row['scheduled_at']) == scheduled_at
    assert row['created_by'] == created_by
    assert row['status'] == "pending"
