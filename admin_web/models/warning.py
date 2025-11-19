"""Warning model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Warning:
    """경고 모델"""
    id: Optional[int]
    user_id: str
    reason: str
    count: int = 1
    admin_name: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reason': self.reason,
            'count': self.count,
            'admin_name': self.admin_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
