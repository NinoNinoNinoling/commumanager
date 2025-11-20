"""Story Event repository"""
from typing import List, Optional
from datetime import datetime, timedelta
from admin_web.models.story_event import StoryEvent, StoryPost
from admin_web.repositories.database import get_economy_db


class StoryEventRepository:
    """스토리 이벤트 데이터 저장소"""

    @staticmethod
    def find_all(page: int = 1, limit: int = 50, status: str = None) -> tuple[List[StoryEvent], int]:
        """이벤트 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            where_clause = "status = ?" if status else "1=1"
            params = [status] if status else []

            cursor.execute(f"SELECT COUNT(*) FROM story_events WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT * FROM story_events
                WHERE {where_clause}
                ORDER BY start_time DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])

            events = [StoryEvent(**dict(row)) for row in cursor.fetchall()]
            return events, total

    @staticmethod
    def find_by_id(event_id: int, include_posts: bool = True) -> Optional[StoryEvent]:
        """ID로 이벤트 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM story_events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            if not row:
                return None

            event = StoryEvent(**dict(row))

            if include_posts:
                event.posts = StoryPostRepository.find_by_event(event_id)

            return event

    @staticmethod
    def create(event: StoryEvent) -> StoryEvent:
        """이벤트 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO story_events (
                    title, description, calendar_event_id, start_time,
                    interval_minutes, status, created_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event.title, event.description, event.calendar_event_id,
                  event.start_time, event.interval_minutes, event.status,
                  event.created_by))
            conn.commit()

            event_id = cursor.lastrowid
            return StoryEventRepository.find_by_id(event_id, include_posts=False)

    @staticmethod
    def update(event: StoryEvent) -> bool:
        """이벤트 수정"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE story_events
                SET title = ?, description = ?, calendar_event_id = ?,
                    start_time = ?, interval_minutes = ?, status = ?
                WHERE id = ?
            """, (event.title, event.description, event.calendar_event_id,
                  event.start_time, event.interval_minutes, event.status,
                  event.id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(event_id: int) -> bool:
        """이벤트 삭제 (CASCADE로 포스트도 함께 삭제됨)"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM story_events WHERE id = ?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def find_pending_events(before_time: datetime = None) -> List[StoryEvent]:
        """대기 중인 이벤트 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            if before_time:
                cursor.execute("""
                    SELECT * FROM story_events
                    WHERE status = 'pending' AND start_time <= ?
                    ORDER BY start_time ASC
                """, (before_time,))
            else:
                cursor.execute("""
                    SELECT * FROM story_events
                    WHERE status = 'pending'
                    ORDER BY start_time ASC
                """)

            return [StoryEvent(**dict(row)) for row in cursor.fetchall()]


class StoryPostRepository:
    """스토리 포스트 데이터 저장소"""

    @staticmethod
    def find_by_event(event_id: int) -> List[StoryPost]:
        """이벤트에 속한 포스트 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM story_posts
                WHERE event_id = ?
                ORDER BY sequence ASC
            """, (event_id,))

            posts = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                row_dict['media_urls'] = StoryPost.media_urls_from_json(row_dict.get('media_urls'))
                posts.append(StoryPost(**row_dict))

            return posts

    @staticmethod
    def find_by_id(post_id: int) -> Optional[StoryPost]:
        """ID로 포스트 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM story_posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            if row:
                row_dict = dict(row)
                row_dict['media_urls'] = StoryPost.media_urls_from_json(row_dict.get('media_urls'))
                return StoryPost(**row_dict)
            return None

    @staticmethod
    def create(post: StoryPost) -> StoryPost:
        """포스트 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            media_urls_json = StoryPost.media_urls_to_json(post.media_urls)
            cursor.execute("""
                INSERT INTO story_posts (
                    event_id, sequence, content, media_urls, status
                )
                VALUES (?, ?, ?, ?, ?)
            """, (post.event_id, post.sequence, post.content,
                  media_urls_json, post.status))
            conn.commit()

            post_id = cursor.lastrowid
            return StoryPostRepository.find_by_id(post_id)

    @staticmethod
    def create_batch(posts: List[StoryPost]) -> List[StoryPost]:
        """포스트 일괄 생성"""
        created = []
        for post in posts:
            created.append(StoryPostRepository.create(post))
        return created

    @staticmethod
    def update(post: StoryPost) -> bool:
        """포스트 수정"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            media_urls_json = StoryPost.media_urls_to_json(post.media_urls)
            cursor.execute("""
                UPDATE story_posts
                SET sequence = ?, content = ?, media_urls = ?, status = ?
                WHERE id = ?
            """, (post.sequence, post.content, media_urls_json, post.status, post.id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(post_id: int) -> bool:
        """포스트 삭제"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM story_posts WHERE id = ?", (post_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_by_event(event_id: int) -> bool:
        """이벤트의 모든 포스트 삭제"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM story_posts WHERE event_id = ?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0
