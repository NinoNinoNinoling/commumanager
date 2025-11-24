"""
OAuthAdmin 모델

OAuth를 통해 로그인 가능한 관리자 계정을 나타냅니다.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OAuthAdmin:
    """
    OAuth 관리자 모델

    Mastodon OAuth를 통해 로그인 가능한 관리자 계정 정보를 저장합니다.

    Attributes:
        id: Primary key
        mastodon_acct: Mastodon 계정 (예: 'admin', 'user@remote.instance')
        display_name: 표시 이름
        added_by: 추가한 관리자 이름
        added_at: 추가된 시각
        is_active: 활성 여부 (False이면 로그인 불가)
        last_login_at: 마지막 로그인 시각
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
            added_at=datetime.fromisoformat(data['added_at']) if data.get('added_at') else None,
            is_active=data.get('is_active', True),
            last_login_at=datetime.fromisoformat(data['last_login_at']) if data.get('last_login_at') else None
        )
