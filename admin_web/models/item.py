"""Item model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Item:
    """아이템 모델"""
    id: Optional[int]
    name: str
    description: Optional[str] = None
    price: int = 0
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
