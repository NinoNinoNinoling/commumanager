"""Calendar service"""
from typing import List, Optional
from admin_web.models.calendar_event import CalendarEvent
from admin_web.repositories.calendar_event_repository import CalendarEventRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository
from admin_web.models.admin_log import AdminLog


class CalendarService:
    """캘린더 비즈니스 로직"""

    def __init__(self):
        self.event_repo = CalendarEventRepository()
        self.admin_log_repo = AdminLogRepository()

    def get_events(self, page: int = 1, limit: int = 50, event_type: str = None) -> dict:
        """이벤트 목록 조회"""
        events, total = self.event_repo.find_all(page, limit, event_type)
        total_pages = (total + limit - 1) // limit

        return {
            'events': [e.to_dict() for e in events],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }

    def get_event(self, event_id: int) -> Optional[CalendarEvent]:
        """이벤트 조회"""
        return self.event_repo.find_by_id(event_id)

    def create_event(self, title: str, description: str = None, event_type: str = 'general',
                     start_date: str = None, end_date: str = None,
                     start_time: str = None, end_time: str = None,
                     admin_name: str = None) -> CalendarEvent:
        """이벤트 생성"""
        # 1. 이벤트 생성
        event = CalendarEvent(
            id=None,
            title=title,
            description=description,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
        )
        created_event = self.event_repo.create(event)

        # 2. 관리자 로그 생성
        if admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='create_event',
                details=f"{title} ({event_type})",
            )
            self.admin_log_repo.create(log)

        return created_event

    def update_event(self, event_id: int, title: str, description: str = None,
                     event_type: str = 'general', start_date: str = None, end_date: str = None,
                     start_time: str = None, end_time: str = None,
                     admin_name: str = None) -> bool:
        """이벤트 수정"""
        event = CalendarEvent(
            id=event_id,
            title=title,
            description=description,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
        )
        success = self.event_repo.update(event)

        # 관리자 로그 생성
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='update_event',
                details=f"{title} (id: {event_id})",
            )
            self.admin_log_repo.create(log)

        return success

    def delete_event(self, event_id: int, admin_name: str = None) -> bool:
        """이벤트 삭제"""
        success = self.event_repo.delete(event_id)

        # 관리자 로그 생성
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='delete_event',
                details=f"event_id: {event_id}",
            )
            self.admin_log_repo.create(log)

        return success
