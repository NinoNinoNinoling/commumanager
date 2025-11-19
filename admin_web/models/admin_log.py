"""Admin Log model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AdminLog:
    """관리자 로그 모델"""
    id: Optional[int]
    admin_name: str
    action_type: str
    target_user: Optional[str] = None
    details: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'admin_name': self.admin_name,
            'action_type': self.action_type,
            'target_user': self.target_user,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if (self.timestamp and isinstance(self.timestamp, datetime)) else self.timestamp,
        }
