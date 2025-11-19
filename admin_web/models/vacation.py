"""Vacation model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Vacation:
    """휴가 모델"""
    id: Optional[int]
    user_id: str
    start_date: datetime
    end_date: datetime
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    reason: Optional[str] = None
    approved: bool = True
    registered_by: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat() if isinstance(self.start_date, datetime) else self.start_date,
            'end_date': self.end_date.isoformat() if isinstance(self.end_date, datetime) else self.end_date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'reason': self.reason,
            'approved': self.approved,
            'registered_by': self.registered_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
