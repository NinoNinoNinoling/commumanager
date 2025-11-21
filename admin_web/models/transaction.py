"""
Transaction 모델

경제 시스템의 금융 거래를 나타냅니다.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """
    사용자 잔액 변경을 추적하는 Transaction 모델

    Attributes:
        id: Primary key (선택, 데이터베이스에서 설정)
        user_id: users.mastodon_id에 대한 Foreign key
        transaction_type: 거래 유형 (reward_settlement, manual_adjust 등)
        amount: 거래 금액 (양수: 입금, 음수: 출금)
        status_id: 연관된 Mastodon 상태 ID (선택)
        item_id: 상점 구매 시 연관된 아이템 ID (선택)
        category: 필터링/분석용 거래 카테고리 (선택)
        description: 사람이 읽을 수 있는 설명 (선택)
        admin_name: 거래를 생성한 관리자 (선택)
        timestamp: 거래 시각 (선택, 데이터베이스에서 설정)
    """
    user_id: str
    transaction_type: str
    amount: int
    id: Optional[int] = None
    status_id: Optional[str] = None
    item_id: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    admin_name: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Transaction을 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            Transaction의 딕셔너리 표현
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'status_id': self.status_id,
            'item_id': self.item_id,
            'category': self.category,
            'description': self.description,
            'admin_name': self.admin_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """
        딕셔너리로부터 Transaction을 생성합니다.

        Args:
            data: 거래 데이터를 담은 딕셔너리

        Returns:
            Transaction 인스턴스
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
            transaction_type=data['transaction_type'],
            amount=data['amount'],
            status_id=data.get('status_id'),
            item_id=data.get('item_id'),
            category=data.get('category'),
            description=data.get('description'),
            admin_name=data.get('admin_name'),
            timestamp=timestamp
        )

    def is_credit(self) -> bool:
        """
        거래가 입금(양수 금액)인지 확인합니다.

        Returns:
            amount > 0이면 True, 아니면 False
        """
        return self.amount > 0

    def is_debit(self) -> bool:
        """
        거래가 출금(음수 금액)인지 확인합니다.

        Returns:
            amount < 0이면 True, 아니면 False
        """
        return self.amount < 0
