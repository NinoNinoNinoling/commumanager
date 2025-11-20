"""Scheduled Announcement service"""
from typing import Optional
from datetime import datetime
from admin_web.models.scheduled_announcement import ScheduledAnnouncement
from admin_web.repositories.scheduled_announcement_repository import ScheduledAnnouncementRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository
from admin_web.models.admin_log import AdminLog


class ScheduledAnnouncementService:
    """공지 예약 비즈니스 로직"""

    def __init__(self):
        self.announcement_repo = ScheduledAnnouncementRepository()
        self.admin_log_repo = AdminLogRepository()

    def get_announcements(self, page: int = 1, limit: int = 50, status: str = None,
                         post_type: str = None) -> dict:
        """공지 목록 조회"""
        announcements, total = self.announcement_repo.find_all(page, limit, status, post_type)
        total_pages = (total + limit - 1) // limit

        return {
            'announcements': [a.to_dict() for a in announcements],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }

    def get_announcement(self, announcement_id: int) -> Optional[ScheduledAnnouncement]:
        """공지 조회"""
        return self.announcement_repo.find_by_id(announcement_id)

    def create_announcement(self, post_type: str, content: str, scheduled_at: str,
                          visibility: str = 'public', is_public: bool = True,
                          admin_name: str = None) -> ScheduledAnnouncement:
        """공지 생성"""
        # 1. 공지 생성
        announcement = ScheduledAnnouncement(
            id=None,
            post_type=post_type,
            content=content,
            scheduled_at=datetime.fromisoformat(scheduled_at.replace('Z', '+00:00')),
            visibility=visibility,
            is_public=is_public,
            status='pending',
            created_by=admin_name or 'admin',
        )
        created_announcement = self.announcement_repo.create(announcement)

        # 2. 관리자 로그 생성
        if admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='create_scheduled_announcement',
                details=f"{post_type} - Scheduled at {scheduled_at}",
            )
            self.admin_log_repo.create(log)

        return created_announcement

    def update_announcement(self, announcement_id: int, post_type: str, content: str,
                          scheduled_at: str, visibility: str = 'public',
                          is_public: bool = True, status: str = 'pending',
                          admin_name: str = None) -> bool:
        """공지 수정"""
        announcement = ScheduledAnnouncement(
            id=announcement_id,
            post_type=post_type,
            content=content,
            scheduled_at=datetime.fromisoformat(scheduled_at.replace('Z', '+00:00')),
            visibility=visibility,
            is_public=is_public,
            status=status,
            created_by=admin_name or 'admin',
        )
        success = self.announcement_repo.update(announcement)

        # 관리자 로그 생성
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='update_scheduled_announcement',
                details=f"announcement_id: {announcement_id}",
            )
            self.admin_log_repo.create(log)

        return success

    def delete_announcement(self, announcement_id: int, admin_name: str = None) -> bool:
        """공지 삭제"""
        success = self.announcement_repo.delete(announcement_id)

        # 관리자 로그 생성
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='delete_scheduled_announcement',
                details=f"announcement_id: {announcement_id}",
            )
            self.admin_log_repo.create(log)

        return success
