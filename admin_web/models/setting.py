"""Setting model"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Setting:
    """설정 모델"""
    key: str
    value: str
    description: Optional[str] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'key': self.key,
            'value': self.value,
            'description': self.description,
        }
