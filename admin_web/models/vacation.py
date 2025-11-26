from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional
from admin_web.utils.datetime_utils import parse_datetime, parse_date, parse_time


@dataclass
class Vacation:
    """
    휴가 기록을 위한 Vacation 모델
    # ...
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
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            start_date=parse_date(data.get('start_date')),
            start_time=parse_time(data.get('start_time')),
            end_date=parse_date(data.get('end_date')),
            end_time=parse_time(data.get('end_time')),
            reason=data.get('reason'),
            approved=data.get('approved', True),
            registered_by=data.get('registered_by'),
            created_at=parse_datetime(data.get('created_at'))
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
