"""
OAuthAdmin 모델

OAuth를 통해 로그인 가능한 관리자 계정을 나타냅니다.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from admin_web.utils.datetime_utils import parse_datetime


@dataclass
class OAuthAdmin:
    """
    OAuth 관리자 모델
    # ...
    """
    mastodon_acct: str
    added_by: str
    id: Optional[int] = None
    display_name: Optional[str] = None
    added_at: Optional[datetime] = None
    is_active: bool = True
    last_login_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        OAuthAdmin을 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            딕셔너리 형태의 관리자 정보
        """
        return {
            'id': self.id,
            'mastodon_acct': self.mastodon_acct,
            'display_name': self.display_name,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'is_active': self.is_active,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }

    @staticmethod
    def from_dict(data: dict) -> 'OAuthAdmin':
        """
        딕셔너리에서 OAuthAdmin 객체를 생성합니다.

        Args:
            data: 관리자 정보 딕셔너리

        Returns:
            OAuthAdmin 객체
        """
        return OAuthAdmin(
            id=data.get('id'),
            mastodon_acct=data['mastodon_acct'],
            display_name=data.get('display_name'),
            added_by=data['added_by'],
            added_at=parse_datetime(data.get('added_at')),
            is_active=data.get('is_active', True),
            last_login_at=parse_datetime(data.get('last_login_at'))
        )
