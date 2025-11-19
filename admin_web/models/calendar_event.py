"""Calendar Event model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CalendarEvent:
    """캘린더 이벤트 모델"""
    id: Optional[int]
    title: str
    description: Optional[str] = None
    event_type: str = 'general'  # general, holiday, community
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'start_date': self.start_date.isoformat() if isinstance(self.start_date, datetime) else self.start_date,
            'end_date': self.end_date.isoformat() if isinstance(self.end_date, datetime) else self.end_date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
