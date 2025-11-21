"""StoryEvent & StoryPost 모델"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class StoryPost:
    event_id: int
    sequence: int
    content: str
    id: Optional[int] = None
    media_urls: Optional[str] = None
    status: str = 'pending'
    mastodon_post_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class StoryEvent:
    title: str
    start_time: datetime
    created_by: str
    id: Optional[int] = None
    description: Optional[str] = None
    interval_minutes: int = 5
    status: str = 'pending'
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    posts: Optional[List[StoryPost]] = None
