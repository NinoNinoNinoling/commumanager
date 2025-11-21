"""CalendarService"""
from typing import List, Dict, Any
from datetime import date

from admin_web.models.calendar_event import CalendarEvent
from admin_web.repositories.calendar_repository import CalendarRepository


class CalendarService:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path
        self.calendar_repo = CalendarRepository(db_path)

    def create_event(self, event: CalendarEvent) -> Dict[str, Any]:
        created = self.calendar_repo.create(event)
        return {'event': created}

    def get_event(self, event_id: int) -> CalendarEvent:
        return self.calendar_repo.find_by_id(event_id)

    def get_events_by_date_range(self, start: date, end: date) -> List[CalendarEvent]:
        return self.calendar_repo.find_by_date_range(start, end)

    def delete_event(self, event_id: int) -> bool:
        event = self.calendar_repo.find_by_id(event_id)
        if not event:
            return False
        self.calendar_repo.delete(event_id)
        return True
