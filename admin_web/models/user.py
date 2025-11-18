"""User model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """유저 모델"""
    mastodon_id: str
    username: str
    display_name: Optional[str] = None
    role: str = 'user'
    dormitory: Optional[str] = None
    balance: int = 0
    total_earned: int = 0
    total_spent: int = 0
    reply_count: int = 0
    last_active: Optional[datetime] = None
    last_check: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def is_admin(self) -> bool:
        """관리자 여부"""
        return self.role == 'admin'

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'mastodon_id': self.mastodon_id,
            'username': self.username,
            'display_name': self.display_name,
            'role': self.role,
            'dormitory': self.dormitory,
            'balance': self.balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'reply_count': self.reply_count,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
