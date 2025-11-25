"""
User 모델

커뮤니티 관리 시스템의 사용자를 나타냅니다.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    경제 및 활동 추적 기능을 가진 User 모델

    Attributes:
        mastodon_id: Primary key, Mastodon 계정 ID (고유값)
        username: Mastodon 유저명 (@username)
        display_name: 표시 이름 (선택)
        role: 사용자 역할 (user, admin, moderator)
        dormitory: 기숙사 배정 (선택)
        balance: 현재 잔액 (갈레온)
        total_earned: 누적 획득 금액
        total_spent: 누적 지출 금액
        reply_count: 총 답글 수
        warning_count: 누적 경고 횟수 (3회 도달 시 자동 아웃)
        is_key_member: 주요 멤버 플래그 (회피 패턴 감지용)
        last_active: 마지막 활동 시각
        last_check: 마지막 체크 시각
        created_at: 계정 생성 시각
        role_name: 마스토돈 역할 이름 (Owner, Admin, 봇 등)
        role_color: 마스토돈 역할 색상 (#ff3838 등)
    """
    mastodon_id: str
    username: str
    display_name: Optional[str] = None
    role: str = 'user'
    dormitory: Optional[str] = None
    balance: int = 0
    total_earned: int = 0
    total_spent: int = 0
    reply_count: int = 0
    warning_count: int = 0
    is_key_member: bool = False
    last_active: Optional[datetime] = None
    last_check: Optional[datetime] = None
    created_at: Optional[datetime] = None
    role_name: Optional[str] = None
    role_color: Optional[str] = None

    def to_dict(self) -> dict:
        """
        User를 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            User의 딕셔너리 표현
        """
        return {
            'mastodon_id': self.mastodon_id,
            'username': self.username,
            'display_name': self.display_name,
            'role': self.role,
            'dormitory': self.dormitory,
            'balance': self.balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'reply_count': self.reply_count,
            'warning_count': self.warning_count,
            'is_key_member': self.is_key_member,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'role_name': self.role_name,
            'role_color': self.role_color,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        딕셔너리로부터 User를 생성합니다.

        Args:
            data: 사용자 데이터를 담은 딕셔너리

        Returns:
            User 인스턴스
        """
        # Parse datetime fields if present
        last_active = None
        if data.get('last_active'):
            if isinstance(data['last_active'], str):
                last_active = datetime.fromisoformat(data['last_active'])
            else:
                last_active = data['last_active']

        last_check = None
        if data.get('last_check'):
            if isinstance(data['last_check'], str):
                last_check = datetime.fromisoformat(data['last_check'])
            else:
                last_check = data['last_check']

        created_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            else:
                created_at = data['created_at']

        return cls(
            mastodon_id=data['mastodon_id'],
            username=data['username'],
            display_name=data.get('display_name'),
            role=data.get('role', 'user'),
            dormitory=data.get('dormitory'),
            balance=data.get('balance', 0),
            total_earned=data.get('total_earned', 0),
            total_spent=data.get('total_spent', 0),
            reply_count=data.get('reply_count', 0),
            warning_count=data.get('warning_count', 0),
            is_key_member=data.get('is_key_member', False),
            last_active=last_active,
            last_check=last_check,
            created_at=created_at,
            role_name=data.get('role_name'),
            role_color=data.get('role_color')
        )

    def has_warnings(self) -> bool:
        """
        사용자가 경고를 받은 적이 있는지 확인합니다.

        Returns:
            warning_count > 0이면 True, 아니면 False
        """
        return self.warning_count > 0

    def is_at_risk_of_ban(self) -> bool:
        """
        사용자가 자동 아웃 위험에 처했는지 확인합니다.

        경고 3회 도달 시 자동 아웃되므로, warning_count == 2일 때 위험 상태입니다.

        Returns:
            warning_count == 2이면 True, 아니면 False
        """
        return self.warning_count == 2
