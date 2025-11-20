"""Scheduled Announcement model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ScheduledAnnouncement:
    """예약된 공지 모델"""
    id: Optional[int]
    post_type: str
    content: str
    scheduled_at: datetime
    visibility: str = 'public'
    is_public: bool = True
    status: str = 'pending'  # pending, published, failed
    mastodon_scheduled_id: Optional[str] = None
    created_by: str = ''
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'post_type': self.post_type,
            'content': self.content,
            'scheduled_at': self.scheduled_at.isoformat() if isinstance(self.scheduled_at, datetime) else self.scheduled_at,
            'visibility': self.visibility,
            'is_public': self.is_public,
            'status': self.status,
            'mastodon_scheduled_id': self.mastodon_scheduled_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }
