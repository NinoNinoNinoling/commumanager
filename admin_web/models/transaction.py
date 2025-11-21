"""
Transaction model

Represents a financial transaction in the economy system.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """
    Transaction model for tracking user balance changes

    Attributes:
        id: Primary key (optional, set by database)
        user_id: Foreign key to users.mastodon_id
        transaction_type: Type of transaction (reward_settlement, manual_adjust, etc.)
        amount: Transaction amount (positive for credit, negative for debit)
        status_id: Related Mastodon status ID (optional)
        item_id: Related item ID for shop purchases (optional)
        category: Transaction category for filtering/analytics (optional)
        description: Human-readable description (optional)
        admin_name: Admin who created the transaction (optional)
        timestamp: Transaction timestamp (optional, set by database)
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
        Convert Transaction to dictionary for JSON serialization

        Returns:
            Dictionary representation of Transaction
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
        Create Transaction from dictionary

        Args:
            data: Dictionary containing transaction data

        Returns:
            Transaction instance
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
        Check if transaction is a credit (positive amount)

        Returns:
            True if amount > 0, False otherwise
        """
        return self.amount > 0

    def is_debit(self) -> bool:
        """
        Check if transaction is a debit (negative amount)

        Returns:
            True if amount < 0, False otherwise
        """
        return self.amount < 0
