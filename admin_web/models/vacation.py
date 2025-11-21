"""
Vacation 모델

사용자의 휴가 정보를 나타냅니다.
"""
from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional


@dataclass
class Vacation:
    """
    휴가 기록을 위한 Vacation 모델

    Attributes:
        id: Primary key (선택, 데이터베이스에서 설정)
        user_id: users.mastodon_id에 대한 Foreign key
        start_date: 휴가 시작일 (필수)
        start_time: 휴가 시작 시간 (선택)
        end_date: 휴가 종료일 (필수)
        end_time: 휴가 종료 시간 (선택)
        reason: 휴가 사유 (선택)
        approved: 승인 여부 (기본값: True)
        registered_by: 등록자 (선택)
        created_at: 생성 시각 (선택, 데이터베이스에서 설정)
    """
    user_id: str
    start_date: date
    end_date: date
    id: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: Optional[str] = None
    approved: bool = True
    registered_by: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Vacation을 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            Vacation의 딕셔너리 표현
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'reason': self.reason,
            'approved': self.approved,
            'registered_by': self.registered_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Vacation':
        """
        딕셔너리로부터 Vacation을 생성합니다.

        Args:
            data: 휴가 데이터를 담은 딕셔너리

        Returns:
            Vacation 인스턴스
        """
        # Parse start_date
        start_date = None
        if data.get('start_date'):
            if isinstance(data['start_date'], str):
                start_date = date.fromisoformat(data['start_date'])
            else:
                start_date = data['start_date']

        # Parse start_time
        start_time = None
        if data.get('start_time'):
            if isinstance(data['start_time'], str):
                start_time = time.fromisoformat(data['start_time'])
            else:
                start_time = data['start_time']

        # Parse end_date
        end_date = None
        if data.get('end_date'):
            if isinstance(data['end_date'], str):
                end_date = date.fromisoformat(data['end_date'])
            else:
                end_date = data['end_date']

        # Parse end_time
        end_time = None
        if data.get('end_time'):
            if isinstance(data['end_time'], str):
                end_time = time.fromisoformat(data['end_time'])
            else:
                end_time = data['end_time']

        # Parse created_at
        created_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            else:
                created_at = data['created_at']

        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            reason=data.get('reason'),
            approved=data.get('approved', True),
            registered_by=data.get('registered_by'),
            created_at=created_at
        )

    def is_approved(self) -> bool:
        """
        휴가가 승인되었는지 확인합니다.

        Returns:
            approved가 True이면 True, 아니면 False
        """
        return self.approved

    def get_duration_days(self) -> int:
        """
        휴가 기간(일수)을 계산합니다.

        종료일 - 시작일 + 1로 계산됩니다.
        (예: 1월 1일~1월 5일 = 5일간)

        Returns:
            휴가 일수
        """
        delta = self.end_date - self.start_date
        return delta.days + 1
