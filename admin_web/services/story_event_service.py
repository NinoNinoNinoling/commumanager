"""StoryEventService"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from admin_web.models.story_event import StoryEvent, StoryPost
from admin_web.repositories.story_event_repository import StoryEventRepository


class StoryEventService:
    def __init__(self, db_path: str = 'economy.db'):
        self.story_repo = StoryEventRepository(db_path)

    def create_event(self, title: str, start_time: datetime, created_by: str, interval_minutes: int = 5) -> Dict[str, Any]:
        event = StoryEvent(title=title, start_time=start_time, created_by=created_by, interval_minutes=interval_minutes)
        created = self.story_repo.create(event)
        return {'event': created}

    def add_posts(self, event_id: int, posts_content: List[str]) -> Dict[str, Any]:
        posts = []
        for seq, content in enumerate(posts_content, start=1):
            post = StoryPost(event_id=event_id, sequence=seq, content=content)
            created_post = self.story_repo.add_post(post)
            posts.append(created_post)
        return {'posts': posts, 'count': len(posts)}
