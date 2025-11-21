"""StoryEventRepository"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from admin_web.models.story_event import StoryEvent, StoryPost


class StoryEventRepository:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, event: StoryEvent) -> StoryEvent:
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
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return StoryEvent(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            start_time=datetime.fromisoformat(row['start_time']),
            interval_minutes=row['interval_minutes'],
            status=row['status'],
            created_by=row['created_by']
        )

    def add_post(self, post: StoryPost) -> StoryPost:
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
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_posts WHERE event_id = ? ORDER BY sequence", (event_id,))
        rows = cursor.fetchall()
        conn.close()
        return [StoryPost(
            id=row['id'],
            event_id=row['event_id'],
            sequence=row['sequence'],
            content=row['content'],
            media_urls=row['media_urls'],
            status=row['status']
        ) for row in rows]
