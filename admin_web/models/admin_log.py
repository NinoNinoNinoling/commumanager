"""AdminLog 모델"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class AdminLog:
    """
    관리자 활동 로그를 나타내는 모델

    admin_logs 테이블의 데이터를 나타냅니다.
    모든 관리자의 주요 활동을 기록하여 투명한 관리를 지원합니다.

    Attributes:
        admin_name: 활동을 수행한 관리자명
        action_type: 활동 유형 (adjust_balance, role_change, warning_add, auto_ban, manual_ban, unban 등)
        id: 로그 ID (Primary key, auto-increment)
        target_user: 대상 유저 ID (유저 관련 활동인 경우)
        details: 활동 상세 설명
        timestamp: 활동 발생 시각 (자동 기록)
    """
    admin_name: str
    action_type: str
    id: Optional[int] = None
    target_user: Optional[str] = None
    details: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        AdminLog를 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            AdminLog의 딕셔너리 표현
        """
        return {
            'id': self.id,
            'admin_name': self.admin_name,
            'action_type': self.action_type,
            'target_user': self.target_user,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdminLog':
        """
        딕셔너리로부터 AdminLog를 생성합니다.

        Args:
            data: 로그 데이터를 담은 딕셔너리

        Returns:
            AdminLog 인스턴스
        """
        timestamp = None
        if data.get('timestamp'):
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'])
            else:
                timestamp = data['timestamp']

        return cls(
            id=data.get('id'),
            admin_name=data['admin_name'],
            action_type=data['action_type'],
            target_user=data.get('target_user'),
            details=data.get('details'),
            timestamp=timestamp,
        )
