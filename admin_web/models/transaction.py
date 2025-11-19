"""Transaction model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """거래 내역 모델"""
    id: Optional[int]
    user_id: str
    transaction_type: str  # earn_reply, earn_attendance, spend_item, admin_adjust
    amount: int
    status_id: Optional[str] = None
    item_id: Optional[int] = None
    description: Optional[str] = None
    admin_name: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'status_id': self.status_id,
            'item_id': self.item_id,
            'description': self.description,
            'admin_name': self.admin_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
