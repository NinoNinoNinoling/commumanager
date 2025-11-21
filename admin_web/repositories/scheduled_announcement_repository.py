"""ScheduledAnnouncementRepository"""
import sqlite3
from typing import Optional
from datetime import datetime
from admin_web.models.scheduled_announcement import ScheduledAnnouncement


class ScheduledAnnouncementRepository:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, announcement: ScheduledAnnouncement) -> ScheduledAnnouncement:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scheduled_posts (post_type, content, scheduled_at, visibility, is_public, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (announcement.post_type, announcement.content, announcement.scheduled_at.isoformat(),
              announcement.visibility, 1 if announcement.is_public else 0, announcement.status, announcement.created_by))
        ann_id = cursor.lastrowid
        conn.commit()
        conn.close()
        announcement.id = ann_id
        return announcement

    def find_by_id(self, ann_id: int) -> Optional[ScheduledAnnouncement]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scheduled_posts WHERE id = ?", (ann_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return ScheduledAnnouncement(
            id=row['id'],
            post_type=row['post_type'],
            content=row['content'],
            scheduled_at=datetime.fromisoformat(row['scheduled_at']),
            visibility=row['visibility'],
            is_public=bool(row['is_public']),
            status=row['status'],
            created_by=row['created_by']
        )
