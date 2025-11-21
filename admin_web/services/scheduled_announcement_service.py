"""ScheduledAnnouncementService"""
from typing import Dict, Any
from datetime import datetime
from admin_web.models.scheduled_announcement import ScheduledAnnouncement
from admin_web.repositories.scheduled_announcement_repository import ScheduledAnnouncementRepository


class ScheduledAnnouncementService:
    """
    예약 공지 관리 비즈니스 로직을 위한 Service

    특정 시각에 자동 발송될 공지사항의 생성 및 관리를 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        self.announcement_repo = ScheduledAnnouncementRepository(db_path)

    def create_announcement(self, post_type: str, content: str, scheduled_at: datetime, created_by: str) -> Dict[str, Any]:
        """
        예약 공지를 생성합니다.

        Args:
            post_type: 포스트 유형 (announcement 등)
            content: 공지 내용
            scheduled_at: 예약 발송 시각
            created_by: 공지 생성자 (관리자명)

        Returns:
            생성된 공지를 담은 딕셔너리 {'announcement': ScheduledAnnouncement}
        """
        announcement = ScheduledAnnouncement(post_type=post_type, content=content, scheduled_at=scheduled_at, created_by=created_by)
        created = self.announcement_repo.create(announcement)
        return {'announcement': created}
