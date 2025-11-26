from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from admin_web.utils.datetime_utils import parse_datetime


@dataclass
class ScheduledAnnouncement:
    """
    예약 발송 공지를 나타내는 모델
    # ...
    """
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
        return cls(
            id=data.get('id'),
            post_type=data['post_type'],
            content=data['content'],
            scheduled_at=parse_datetime(data.get('scheduled_at')),
            visibility=data.get('visibility', 'public'),
            is_public=data.get('is_public', True),
            status=data.get('status', 'pending'),
            created_by=data['created_by'],
            mastodon_scheduled_id=data.get('mastodon_scheduled_id'),
            created_at=parse_datetime(data.get('created_at')),
            published_at=parse_datetime(data.get('published_at')),
        )
