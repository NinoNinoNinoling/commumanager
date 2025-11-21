"""CalendarEvent 모델"""
from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional


@dataclass
class CalendarEvent:
    """
    커뮤니티 일정 및 이벤트를 나타내는 모델

    calendar_events 테이블의 데이터를 나타냅니다.
    커뮤니티 일정, 공휴일, 리뉴얼 기간 등을 관리합니다.

    Attributes:
        title: 이벤트 제목
        event_date: 이벤트 시작 날짜
        created_by: 이벤트 생성자 (관리자명)
        id: 이벤트 ID (Primary key, auto-increment)
        description: 이벤트 설명
        start_time: 이벤트 시작 시각 (선택사항)
        end_date: 이벤트 종료 날짜 (선택사항, 기간 이벤트인 경우)
        end_time: 이벤트 종료 시각 (선택사항)
        event_type: 이벤트 유형 (event, holiday, community 등)
        is_global_vacation: 리뉴얼 기간 여부 (True 시 전체 유저 휴식 처리)
        created_at: 생성 시각
        updated_at: 수정 시각
    """
    title: str
    event_date: date
    created_by: str
    id: Optional[int] = None
    description: Optional[str] = None
    start_time: Optional[time] = None
    end_date: Optional[date] = None
    end_time: Optional[time] = None
    event_type: str = 'event'
    is_global_vacation: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'event_type': self.event_type,
            'is_global_vacation': self.is_global_vacation,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CalendarEvent':
        return cls(
            id=data.get('id'),
            title=data['title'],
            description=data.get('description'),
            event_date=date.fromisoformat(data['event_date']) if isinstance(data.get('event_date'), str) else data.get('event_date'),
            start_time=time.fromisoformat(data['start_time']) if isinstance(data.get('start_time'), str) else data.get('start_time'),
            end_date=date.fromisoformat(data['end_date']) if isinstance(data.get('end_date'), str) else data.get('end_date'),
            end_time=time.fromisoformat(data['end_time']) if isinstance(data.get('end_time'), str) else data.get('end_time'),
            event_type=data.get('event_type', 'event'),
            is_global_vacation=data.get('is_global_vacation', False),
            created_by=data['created_by'],
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at'),
            updated_at=datetime.fromisoformat(data['updated_at']) if isinstance(data.get('updated_at'), str) else data.get('updated_at')
        )

    def is_multi_day(self) -> bool:
        return self.end_date is not None and self.end_date != self.event_date
