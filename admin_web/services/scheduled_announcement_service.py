"""ScheduledAnnouncementService"""
from typing import Dict, Any
from datetime import datetime
from admin_web.models.scheduled_announcement import ScheduledAnnouncement
from admin_web.repositories.scheduled_announcement_repository import ScheduledAnnouncementRepository


class ScheduledAnnouncementService:
    def __init__(self, db_path: str = 'economy.db'):
        self.announcement_repo = ScheduledAnnouncementRepository(db_path)

    def create_announcement(self, post_type: str, content: str, scheduled_at: datetime, created_by: str) -> Dict[str, Any]:
        announcement = ScheduledAnnouncement(post_type=post_type, content=content, scheduled_at=scheduled_at, created_by=created_by)
        created = self.announcement_repo.create(announcement)
        return {'announcement': created}
