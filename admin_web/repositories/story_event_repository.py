"""
StoryEventRepository

story_events 및 story_posts 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from admin_web.models.story_event import StoryEvent, StoryPost
from admin_web.utils.datetime_utils import parse_datetime


class StoryEventRepository:
    """
    StoryEvent 및 StoryPost 데이터 접근을 위한 Repository

    story_events와 story_posts 테이블에 대한 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        StoryEventRepository를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """
        Row factory가 설정된 데이터베이스 연결을 가져옵니다.

        Returns:
            SQLite 연결 객체
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_story_event(self, row: sqlite3.Row) -> StoryEvent:
        """
        데이터베이스 row를 StoryEvent 모델로 변환합니다.
        """
        return StoryEvent(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            start_time=parse_datetime(row['start_time']),
            interval_minutes=row['interval_minutes'],
            status=row['status'],
            created_by=row['created_by'],
            created_at=parse_datetime(row['created_at']),
            published_at=parse_datetime(row['published_at'])
        )

    def _row_to_story_post(self, row: sqlite3.Row) -> StoryPost:
        """
        데이터베이스 row를 StoryPost 모델로 변환합니다.
        """
        return StoryPost(
            id=row['id'],
            event_id=row['event_id'],
            sequence=row['sequence'],
            content=row['content'],
            media_urls=row['media_urls'],
            status=row['status'],
            mastodon_post_id=row['mastodon_post_id'],
            scheduled_at=parse_datetime(row['scheduled_at']),
            published_at=parse_datetime(row['published_at']),
            error_message=row['error_message']
        )

    def create(self, event: StoryEvent) -> StoryEvent:
        """
        새 스토리 이벤트를 생성합니다.

        Args:
            event: 생성할 StoryEvent 인스턴스

        Returns:
            ID가 포함된 생성된 이벤트
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO story_events (title, description, start_time, interval_minutes, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event.title, event.description, event.start_time.isoformat(), event.interval_minutes, event.status, event.created_by))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        event.id = event_id
        return event

    def find_by_id(self, event_id: int) -> Optional[StoryEvent]:
        """
        ID로 스토리 이벤트를 조회합니다.

        Args:
            event_id: 이벤트 ID

        Returns:
            찾은 경우 StoryEvent, 아니면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return self._row_to_story_event(row)

    def add_post(self, post: StoryPost) -> StoryPost:
        """
        스토리 이벤트에 포스트를 추가합니다.

        Args:
            post: 추가할 StoryPost 인스턴스

        Returns:
            ID가 포함된 생성된 포스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO story_posts (event_id, sequence, content, media_urls, status)
            VALUES (?, ?, ?, ?, ?)
        """, (post.event_id, post.sequence, post.content, post.media_urls, post.status))
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        post.id = post_id
        return post

    def find_posts_by_event(self, event_id: int) -> List[StoryPost]:
        """
        특정 이벤트의 모든 포스트를 조회합니다.

        Args:
            event_id: 스토리 이벤트 ID

        Returns:
            이벤트에 속한 포스트 리스트 (sequence 순서)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_posts WHERE event_id = ? ORDER BY sequence", (event_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_story_post(row) for row in rows]

