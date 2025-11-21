"""StoryEvent & StoryPost 모델"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class StoryPost:
    event_id: int
    sequence: int
    content: str
    id: Optional[int] = None
    media_urls: Optional[str] = None
    status: str = 'pending'
    mastodon_post_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        StoryPost를 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            StoryPost의 딕셔너리 표현
        """
        return {
            'id': self.id,
            'event_id': self.event_id,
            'sequence': self.sequence,
            'content': self.content,
            'media_urls': self.media_urls,
            'status': self.status,
            'mastodon_post_id': self.mastodon_post_id,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'error_message': self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryPost':
        """
        딕셔너리로부터 StoryPost를 생성합니다.

        Args:
            data: 포스트 데이터를 담은 딕셔너리

        Returns:
            StoryPost 인스턴스
        """
        scheduled_at = None
        if data.get('scheduled_at'):
            if isinstance(data['scheduled_at'], str):
                scheduled_at = datetime.fromisoformat(data['scheduled_at'])
            else:
                scheduled_at = data['scheduled_at']

        published_at = None
        if data.get('published_at'):
            if isinstance(data['published_at'], str):
                published_at = datetime.fromisoformat(data['published_at'])
            else:
                published_at = data['published_at']

        return cls(
            id=data.get('id'),
            event_id=data['event_id'],
            sequence=data['sequence'],
            content=data['content'],
            media_urls=data.get('media_urls'),
            status=data.get('status', 'pending'),
            mastodon_post_id=data.get('mastodon_post_id'),
            scheduled_at=scheduled_at,
            published_at=published_at,
            error_message=data.get('error_message'),
        )


@dataclass
class StoryEvent:
    title: str
    start_time: datetime
    created_by: str
    id: Optional[int] = None
    description: Optional[str] = None
    interval_minutes: int = 5
    status: str = 'pending'
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    posts: Optional[List[StoryPost]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        StoryEvent를 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            StoryEvent의 딕셔너리 표현
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'interval_minutes': self.interval_minutes,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'posts': [post.to_dict() for post in self.posts] if self.posts else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryEvent':
        """
        딕셔너리로부터 StoryEvent를 생성합니다.

        Args:
            data: 이벤트 데이터를 담은 딕셔너리

        Returns:
            StoryEvent 인스턴스
        """
        start_time = None
        if data.get('start_time'):
            if isinstance(data['start_time'], str):
                start_time = datetime.fromisoformat(data['start_time'])
            else:
                start_time = data['start_time']

        created_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            else:
                created_at = data['created_at']

        published_at = None
        if data.get('published_at'):
            if isinstance(data['published_at'], str):
                published_at = datetime.fromisoformat(data['published_at'])
            else:
                published_at = data['published_at']

        posts = None
        if data.get('posts'):
            posts = [StoryPost.from_dict(post) for post in data['posts']]

        return cls(
            id=data.get('id'),
            title=data['title'],
            description=data.get('description'),
            start_time=start_time,
            interval_minutes=data.get('interval_minutes', 5),
            status=data.get('status', 'pending'),
            created_by=data['created_by'],
            created_at=created_at,
            published_at=published_at,
            posts=posts,
        )
