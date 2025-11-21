"""Phase 4 통합 테스트"""
import sqlite3
import pytest
from datetime import date, time


@pytest.fixture
def calendar_service(temp_db):
    from init_db import initialize_database
    from admin_web.services.calendar_service import CalendarService
    initialize_database(temp_db)
    return CalendarService(temp_db)


def test_phase4_calendar_integration(calendar_service):
    from admin_web.models.calendar_event import CalendarEvent
    
    # Create event
    event = CalendarEvent(
        title='리뉴얼 기간',
        event_date=date(2025, 1, 1),
        end_date=date(2025, 1, 7),
        event_type='renewal',
        is_global_vacation=True,
        created_by='admin'
    )
    result = calendar_service.create_event(event)
    assert result['event'].id is not None
    
    # Get event
    retrieved = calendar_service.get_event(result['event'].id)
    assert retrieved.title == '리뉴얼 기간'
    assert retrieved.is_multi_day() is True
    
    # Get by date range
    events = calendar_service.get_events_by_date_range(date(2025, 1, 1), date(2025, 1, 31))
    assert len(events) == 1
    
    # Delete event
    deleted = calendar_service.delete_event(result['event'].id)
    assert deleted is True
    
    print("✅ Phase 4 통합 테스트 성공!")
