"""StoryEvent & StoryPost 모델"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from admin_web.utils.datetime_utils import parse_datetime


@dataclass
class StoryPost:
    """
    스토리 이벤트에 포함된 개별 포스트를 나타내는 모델

    story_posts 테이블의 데이터를 나타냅니다.
    여러 개의 포스트를 일정 간격으로 자동 발송하는 스토리 이벤트의 구성 요소입니다.

    Attributes:
        event_id: 스토리 이벤트 ID (Foreign key to story_events)
        sequence: 포스트 순서 (1부터 시작)
        content: 포스트 내용
        id: 포스트 ID (Primary key, auto-increment)
        media_urls: 첨부 미디어 URL (JSON 문자열)
        status: 발송 상태 (pending, published, failed)
        mastodon_post_id: 마스토돈에 발행된 포스트 ID
        scheduled_at: 예약 발송 시각
        published_at: 실제 발송 시각
        error_message: 발송 실패 시 에러 메시지
    """
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
        return cls(
            id=data.get('id'),
            event_id=data['event_id'],
            sequence=data['sequence'],
            content=data['content'],
            media_urls=data.get('media_urls'),
            status=data.get('status', 'pending'),
            mastodon_post_id=data.get('mastodon_post_id'),
            scheduled_at=parse_datetime(data.get('scheduled_at')),
            published_at=parse_datetime(data.get('published_at')),
            error_message=data.get('error_message'),
        )


@dataclass
class StoryEvent:
    """
    여러 포스트를 일정 간격으로 자동 발송하는 스토리 이벤트 모델

    story_events 테이블의 데이터를 나타냅니다.
    하나의 이벤트는 여러 개의 StoryPost를 포함하며, 설정된 간격으로 자동 발송됩니다.

    Attributes:
        title: 이벤트 제목
        start_time: 첫 번째 포스트 발송 시각
        created_by: 이벤트 생성자 (관리자명)
        id: 이벤트 ID (Primary key, auto-increment)
        description: 이벤트 설명
        interval_minutes: 포스트 간 발송 간격 (분 단위, 기본값: 5분)
        status: 이벤트 상태 (pending, in_progress, completed, failed)
        created_at: 이벤트 생성 시각
        published_at: 첫 번째 포스트 발송 시각 (실제 발송 시작 시각)
        posts: 이벤트에 포함된 포스트 목록
    """
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
        posts = None
        if data.get('posts'):
            posts = [StoryPost.from_dict(post) for post in data['posts']]

        return cls(
            id=data.get('id'),
            title=data['title'],
            description=data.get('description'),
            start_time=parse_datetime(data.get('start_time')),
            interval_minutes=data.get('interval_minutes', 5),
            status=data.get('status', 'pending'),
            created_by=data['created_by'],
            created_at=parse_datetime(data.get('created_at')),
            published_at=parse_datetime(data.get('published_at')),
            posts=posts,
        )
