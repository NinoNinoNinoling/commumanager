"""
Setting 모델
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Setting:
    """
    시스템 설정을 위한 Setting 모델

    Attributes:
        key: Primary key, 설정의 고유 키
        value: 설정 값
        description: 설정에 대한 설명
        updated_at: 마지막 업데이트 시각
        updated_by: 마지막으로 수정한 관리자
    """
    key: str
    value: str
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Setting":
        updated_at = None
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'])
            else:
                updated_at = data['updated_at']

        return cls(
            key=data["key"],
            value=data["value"],
            description=data.get("description"),
            updated_at=updated_at,
            updated_by=data.get("updated_by"),
        )
