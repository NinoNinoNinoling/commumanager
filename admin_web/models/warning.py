"""
Warning 모델

활동량/고립/편향/회피에 대한 유저 경고를 나타냅니다.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Warning:
    """
    사용자 활동 모니터링을 위한 Warning 모델

    Attributes:
        id: Primary key (선택, 데이터베이스에서 설정)
        user_id: users.mastodon_id에 대한 Foreign key
        warning_type: 경고 유형 (activity, isolation, bias, avoidance)
        check_period_hours: 체크 기간 (시간 단위, 예: 48)
        required_replies: 필요한 답글 수
        actual_replies: 실제 발견된 답글 수
        message: 유저에게 전송된 경고 메시지
        dm_sent: DM 전송 성공 여부
        admin_name: 경고를 발행한 관리자 (자동의 경우 'system')
        timestamp: 경고 시각 (선택, 데이터베이스에서 설정)
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
        Warning을 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            Warning의 딕셔너리 표현
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
        딕셔너리로부터 Warning을 생성합니다.

        Args:
            data: 경고 데이터를 담은 딕셔너리

        Returns:
            Warning 인스턴스
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
        활동량 부족 경고인지 확인합니다.

        Returns:
            warning_type == 'activity'이면 True, 아니면 False
        """
        return self.warning_type == 'activity'

    def is_isolation_warning(self) -> bool:
        """
        고립 위험 경고인지 확인합니다.

        Returns:
            warning_type == 'isolation'이면 True, 아니면 False
        """
        return self.warning_type == 'isolation'

    def has_dm_sent(self) -> bool:
        """
        DM 전송 성공 여부를 확인합니다.

        Returns:
            dm_sent가 True이면 True, 아니면 False
        """
        return self.dm_sent
