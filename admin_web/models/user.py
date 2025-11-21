"""
User model

Represents a user in the community management system.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    User model with economy and activity tracking

    Attributes:
        mastodon_id: Primary key, unique Mastodon account ID
        username: Mastodon username (@username)
        display_name: Display name (optional)
        role: User role (user, admin, moderator)
        dormitory: Dormitory assignment (optional)
        balance: Current balance in Galleons
        total_earned: Cumulative earned amount
        total_spent: Cumulative spent amount
        reply_count: Total reply count
        warning_count: Cumulative warning count (auto-ban at 3)
        is_key_member: Key member flag (for avoidance pattern detection)
        last_active: Last activity timestamp
        last_check: Last check timestamp
        created_at: Account creation timestamp
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

    def to_dict(self) -> dict:
        """
        Convert User to dictionary for JSON serialization

        Returns:
            Dictionary representation of User
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
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        Create User from dictionary

        Args:
            data: Dictionary containing user data

        Returns:
            User instance
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
            created_at=created_at
        )

    def has_warnings(self) -> bool:
        """
        Check if user has received any warnings

        Returns:
            True if warning_count > 0, False otherwise
        """
        return self.warning_count > 0

    def is_at_risk_of_ban(self) -> bool:
        """
        Check if user is at risk of automatic ban

        User is auto-banned at 3 warnings, so at risk when warning_count == 2

        Returns:
            True if warning_count == 2, False otherwise
        """
        return self.warning_count == 2
