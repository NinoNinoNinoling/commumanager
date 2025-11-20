"""Scheduled Announcement repository"""
from typing import List, Optional
from datetime import datetime
from admin_web.models.scheduled_announcement import ScheduledAnnouncement
from admin_web.repositories.database import get_economy_db


class ScheduledAnnouncementRepository:
    """예약된 공지 데이터 저장소"""

    @staticmethod
    def find_all(page: int = 1, limit: int = 50, status: str = None, post_type: str = None) -> tuple[List[ScheduledAnnouncement], int]:
        """공지 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # WHERE 조건
            where_parts = []
            params = []

            if status:
                where_parts.append("status = ?")
                params.append(status)
            if post_type:
                where_parts.append("post_type = ?")
                params.append(post_type)

            where_clause = " AND ".join(where_parts) if where_parts else "1=1"

            # 전체 개수
            cursor.execute(f"SELECT COUNT(*) FROM scheduled_posts WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT * FROM scheduled_posts
                WHERE {where_clause}
                ORDER BY scheduled_at DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])

            announcements = [ScheduledAnnouncement(**dict(row)) for row in cursor.fetchall()]
            return announcements, total

    @staticmethod
    def find_by_id(announcement_id: int) -> Optional[ScheduledAnnouncement]:
        """ID로 공지 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scheduled_posts WHERE id = ?", (announcement_id,))
            row = cursor.fetchone()
            if row:
                return ScheduledAnnouncement(**dict(row))
            return None

    @staticmethod
    def find_pending_announcements(before_time: datetime = None) -> List[ScheduledAnnouncement]:
        """대기 중인 공지 조회 (예약 시간이 지난 것들)"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            if before_time:
                cursor.execute("""
                    SELECT * FROM scheduled_posts
                    WHERE status = 'pending' AND scheduled_at <= ?
                    ORDER BY scheduled_at ASC
                """, (before_time,))
            else:
                cursor.execute("""
                    SELECT * FROM scheduled_posts
                    WHERE status = 'pending'
                    ORDER BY scheduled_at ASC
                """)

            return [ScheduledAnnouncement(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def create(announcement: ScheduledAnnouncement) -> ScheduledAnnouncement:
        """공지 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scheduled_posts (
                    post_type, content, scheduled_at, visibility, is_public,
                    status, created_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (announcement.post_type, announcement.content, announcement.scheduled_at,
                  announcement.visibility, announcement.is_public, announcement.status,
                  announcement.created_by))
            conn.commit()

            # 생성된 ID로 조회
            announcement_id = cursor.lastrowid
            return ScheduledAnnouncementRepository.find_by_id(announcement_id)

    @staticmethod
    def update(announcement: ScheduledAnnouncement) -> bool:
        """공지 수정"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scheduled_posts
                SET post_type = ?, content = ?, scheduled_at = ?,
                    visibility = ?, is_public = ?, status = ?
                WHERE id = ?
            """, (announcement.post_type, announcement.content, announcement.scheduled_at,
                  announcement.visibility, announcement.is_public, announcement.status,
                  announcement.id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def update_status(announcement_id: int, status: str, mastodon_id: str = None,
                     published_at: datetime = None) -> bool:
        """공지 상태 업데이트"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scheduled_posts
                SET status = ?, mastodon_scheduled_id = ?, published_at = ?
                WHERE id = ?
            """, (status, mastodon_id, published_at, announcement_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(announcement_id: int) -> bool:
        """공지 삭제"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scheduled_posts WHERE id = ?", (announcement_id,))
            conn.commit()
            return cursor.rowcount > 0
