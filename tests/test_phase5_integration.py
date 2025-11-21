"""Phase 5 통합 테스트"""
import sqlite3
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def story_service(temp_db):
    from init_db import initialize_database
    from admin_web.services.story_event_service import StoryEventService
    initialize_database(temp_db)
    return StoryEventService(temp_db)


@pytest.fixture
def announcement_service(temp_db):
    from init_db import initialize_database
    from admin_web.services.scheduled_announcement_service import ScheduledAnnouncementService
    initialize_database(temp_db)
    return ScheduledAnnouncementService(temp_db)


def test_story_event_integration(story_service):
    # Create story event
    result = story_service.create_event(
        title='연재 스토리',
        start_time=datetime(2025, 1, 1, 10, 0),
        created_by='admin',
        interval_minutes=10
    )
    assert result['event'].id is not None
    
    # Add posts
    posts_result = story_service.add_posts(
        event_id=result['event'].id,
        posts_content=['첫 번째 포스트', '두 번째 포스트', '세 번째 포스트']
    )
    assert posts_result['count'] == 3
    print("✅ Story Event 통합 테스트 성공!")


def test_scheduled_announcement_integration(announcement_service):
    # Create announcement
    result = announcement_service.create_announcement(
        post_type='notice',
        content='중요 공지사항',
        scheduled_at=datetime(2025, 1, 1, 12, 0),
        created_by='admin'
    )
    assert result['announcement'].id is not None
    assert result['announcement'].status == 'pending'
    print("✅ Scheduled Announcement 통합 테스트 성공!")
