"""CalendarService"""
from typing import List, Dict, Any
from datetime import date

from admin_web.models.calendar_event import CalendarEvent
from admin_web.repositories.calendar_repository import CalendarRepository


class CalendarService:
    """
    일정 관리 비즈니스 로직을 위한 Service

    커뮤니티 일정, 공휴일, 리뉴얼 기간 등의 생성, 조회, 삭제를 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path
        self.calendar_repo = CalendarRepository(db_path)

    def create_event(self, event: CalendarEvent) -> Dict[str, Any]:
        """
        일정 이벤트를 생성합니다.

        Args:
            event: 생성할 CalendarEvent 객체

        Returns:
            생성된 이벤트를 담은 딕셔너리 {'event': CalendarEvent}
        """
        created = self.calendar_repo.create(event)
        return {'event': created}

    def get_event(self, event_id: int) -> CalendarEvent:
        """
        ID로 일정 이벤트를 조회합니다.

        Args:
            event_id: 조회할 이벤트 ID

        Returns:
            조회된 CalendarEvent 객체
        """
        return self.calendar_repo.find_by_id(event_id)

    def get_events_by_date_range(self, start: date, end: date) -> List[CalendarEvent]:
        """
        기간 내 일정 이벤트 목록을 조회합니다.

        Args:
            start: 조회 시작 날짜
            end: 조회 종료 날짜

        Returns:
            해당 기간의 CalendarEvent 목록
        """
        return self.calendar_repo.find_by_date_range(start, end)

    def delete_event(self, event_id: int) -> bool:
        """
        일정 이벤트를 삭제합니다.

        Args:
            event_id: 삭제할 이벤트 ID

        Returns:
            삭제 성공 시 True, 이벤트가 없으면 False
        """
        event = self.calendar_repo.find_by_id(event_id)
        if not event:
            return False
        self.calendar_repo.delete(event_id)
        return True
