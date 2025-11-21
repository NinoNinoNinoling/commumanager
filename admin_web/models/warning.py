"""
Warning model

Represents a warning issued to a user for activity/isolation/bias/avoidance.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Warning:
    """
    Warning model for user activity monitoring

    Attributes:
        id: Primary key (optional, set by database)
        user_id: Foreign key to users.mastodon_id
        warning_type: Type of warning (activity, isolation, bias, avoidance)
        check_period_hours: Period checked in hours (e.g., 48)
        required_replies: Required number of replies
        actual_replies: Actual number of replies found
        message: Warning message sent to user
        dm_sent: Whether DM was successfully sent
        admin_name: Admin who issued the warning (or 'system' for auto)
        timestamp: Warning timestamp (optional, set by database)
    """
    user_id: str
    warning_type: str
    id: Optional[int] = None
    check_period_hours: Optional[int] = None
    required_replies: Optional[int] = None
    actual_replies: Optional[int] = None
    message: Optional[str] = None
    dm_sent: bool = False
    admin_name: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Convert Warning to dictionary for JSON serialization

        Returns:
            Dictionary representation of Warning
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'warning_type': self.warning_type,
            'check_period_hours': self.check_period_hours,
            'required_replies': self.required_replies,
            'actual_replies': self.actual_replies,
            'message': self.message,
            'dm_sent': self.dm_sent,
            'admin_name': self.admin_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Warning':
        """
        Create Warning from dictionary

        Args:
            data: Dictionary containing warning data

        Returns:
            Warning instance
        """
        # Parse timestamp if present
        timestamp = None
        if data.get('timestamp'):
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'])
            else:
                timestamp = data['timestamp']

        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            warning_type=data['warning_type'],
            check_period_hours=data.get('check_period_hours'),
            required_replies=data.get('required_replies'),
            actual_replies=data.get('actual_replies'),
            message=data.get('message'),
            dm_sent=data.get('dm_sent', False),
            admin_name=data.get('admin_name'),
            timestamp=timestamp
        )

    def is_activity_warning(self) -> bool:
        """
        Check if this is an activity warning

        Returns:
            True if warning_type == 'activity', False otherwise
        """
        return self.warning_type == 'activity'

    def is_isolation_warning(self) -> bool:
        """
        Check if this is an isolation warning

        Returns:
            True if warning_type == 'isolation', False otherwise
        """
        return self.warning_type == 'isolation'

    def has_dm_sent(self) -> bool:
        """
        Check if DM was successfully sent

        Returns:
            True if dm_sent is True, False otherwise
        """
        return self.dm_sent
