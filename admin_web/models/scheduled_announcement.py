"""ScheduledAnnouncement 모델"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class ScheduledAnnouncement:
    post_type: str
    content: str
    scheduled_at: datetime
    created_by: str
    id: Optional[int] = None
    visibility: str = 'public'
    is_public: bool = True
    status: str = 'pending'
    mastodon_scheduled_id: Optional[str] = None
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        ScheduledAnnouncement를 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            ScheduledAnnouncement의 딕셔너리 표현
        """
        return {
            'id': self.id,
            'post_type': self.post_type,
            'content': self.content,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'visibility': self.visibility,
            'is_public': self.is_public,
            'status': self.status,
            'created_by': self.created_by,
            'mastodon_scheduled_id': self.mastodon_scheduled_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledAnnouncement':
        """
        딕셔너리로부터 ScheduledAnnouncement를 생성합니다.

        Args:
            data: 공지 데이터를 담은 딕셔너리

        Returns:
            ScheduledAnnouncement 인스턴스
        """
        scheduled_at = None
        if data.get('scheduled_at'):
            if isinstance(data['scheduled_at'], str):
                scheduled_at = datetime.fromisoformat(data['scheduled_at'])
            else:
                scheduled_at = data['scheduled_at']

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

        return cls(
            id=data.get('id'),
            post_type=data['post_type'],
            content=data['content'],
            scheduled_at=scheduled_at,
            visibility=data.get('visibility', 'public'),
            is_public=data.get('is_public', True),
            status=data.get('status', 'pending'),
            created_by=data['created_by'],
            mastodon_scheduled_id=data.get('mastodon_scheduled_id'),
            created_at=created_at,
            published_at=published_at,
        )
