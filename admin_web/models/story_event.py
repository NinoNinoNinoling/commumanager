"""Story Event model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class StoryEvent:
    """스토리 이벤트 모델 (여러 포스트를 묶는 단위)"""
    id: Optional[int]
    title: str
    description: Optional[str] = None
    calendar_event_id: Optional[int] = None  # 연결된 일정 (선택)
    start_time: Optional[datetime] = None
    interval_minutes: int = 5  # 포스트 간 간격 (분)
    status: str = 'pending'  # pending, in_progress, completed, failed
    created_by: str = ''
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    posts: Optional[List['StoryPost']] = None  # 이벤트에 속한 포스트들

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'calendar_event_id': self.calendar_event_id,
            'start_time': self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            'interval_minutes': self.interval_minutes,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }
        if self.posts is not None:
            result['posts'] = [p.to_dict() for p in self.posts]
        return result


@dataclass
class StoryPost:
    """스토리 개별 포스트 모델"""
    id: Optional[int]
    event_id: int
    sequence: int  # 포스트 순서 (1, 2, 3, ...)
    content: str
    media_urls: Optional[List[str]] = None
    status: str = 'pending'  # pending, published, failed
    mastodon_post_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'event_id': self.event_id,
            'sequence': self.sequence,
            'content': self.content,
            'media_urls': self.media_urls,
            'status': self.status,
            'mastodon_post_id': self.mastodon_post_id,
            'scheduled_at': self.scheduled_at.isoformat() if isinstance(self.scheduled_at, datetime) else self.scheduled_at,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'error_message': self.error_message,
        }

    @staticmethod
    def media_urls_to_json(media_urls: Optional[List[str]]) -> Optional[str]:
        """미디어 URL 리스트를 JSON 문자열로 변환"""
        if not media_urls:
            return None
        import json
        return json.dumps(media_urls)

    @staticmethod
    def media_urls_from_json(json_str: Optional[str]) -> Optional[List[str]]:
        """JSON 문자열을 미디어 URL 리스트로 변환"""
        if not json_str:
            return None
        try:
            import json
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return None
