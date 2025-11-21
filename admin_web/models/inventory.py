"""Inventory 모델"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Inventory:
    """유저의 아이템 보유 정보"""
    user_id: str
    item_id: int
    id: Optional[int] = None
    quantity: int = 1
    acquired_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'acquired_at': self.acquired_at.isoformat() if self.acquired_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Inventory':
        acquired_at = None
        if data.get('acquired_at'):
            if isinstance(data['acquired_at'], str):
                acquired_at = datetime.fromisoformat(data['acquired_at'])
            else:
                acquired_at = data['acquired_at']
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            item_id=data['item_id'],
            quantity=data.get('quantity', 1),
            acquired_at=acquired_at
        )
