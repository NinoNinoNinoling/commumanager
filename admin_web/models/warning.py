"""Warning model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Warning:
    """경고 모델"""
    id: Optional[int]
    user_id: str
    warning_type: str = 'auto'
    check_period_hours: Optional[int] = None
    required_replies: Optional[int] = None
    actual_replies: Optional[int] = None
    message: Optional[str] = None
    dm_sent: bool = False
    admin_name: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'warning_type': self.warning_type,
            'check_period_hours': self.check_period_hours,
            'required_replies': self.required_replies,
            'actual_replies': self.actual_replies,
            'message': self.message,
            'dm_sent': self.dm_sent,
            'admin_name': self.admin_name,
            'timestamp': self.timestamp.isoformat() if (self.timestamp and isinstance(self.timestamp, datetime)) else self.timestamp,
        }
