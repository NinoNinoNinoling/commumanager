"""ScheduledAnnouncement 모델"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ScheduledAnnouncement:
    post_type: str
    content: str
    scheduled_at: datetime
    created_by: str
    id: Optional[int] = None
    visibility: str = 'public'
    is_public: bool = True
    status: str = 'pending'
    mastodon_scheduled_id: Optional[str] = None
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
