"""
UserService

Business logic layer for user management
"""
from typing import List, Optional, Dict
from datetime import datetime

from admin_web.models.user import User
from admin_web.models.transaction import Transaction
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository


class UserService:
    """
    Service for user management business logic

    Handles:
    - User CRUD operations
    - Role management with validation
    - Balance adjustments with transaction creation
    - User statistics
    """

    VALID_ROLES = {'user', 'admin', 'moderator'}

    def __init__(self, db_path: str = 'economy.db'):
        """
        Initialize UserService

        Args:
            db_path: Path to SQLite database file
        """
        self.user_repo = UserRepository(db_path)
        self.transaction_repo = TransactionRepository(db_path)
        self.db_path = db_path

    def get_user(self, mastodon_id: str) -> Optional[User]:
        """
        Get user by Mastodon ID

        Args:
            mastodon_id: User's Mastodon ID

        Returns:
            User if found, None otherwise
        """
        return self.user_repo.find_by_id(mastodon_id)

    def get_all_users(self) -> List[User]:
        """
        Get all users

        Returns:
            List of all users
        """
        return self.user_repo.find_all()

    def create_user(
        self,
        mastodon_id: str,
        username: str,
        display_name: Optional[str] = None,
        role: str = 'user'
    ) -> User:
        """
        Create new user

        Args:
            mastodon_id: User's Mastodon ID
            username: Username
            display_name: Display name (optional)
            role: User role (default: 'user')

        Returns:
            Created user

        Raises:
            ValueError: If role is invalid
        """
        if role not in self.VALID_ROLES:
            raise ValueError(f'Invalid role: {role}. Must be one of {self.VALID_ROLES}')

        user = User(
            mastodon_id=mastodon_id,
            username=username,
            display_name=display_name,
            role=role,
            balance=0,
            total_earned=0,
            total_spent=0,
            reply_count=0,
            warning_count=0,
            is_key_member=False
        )

        return self.user_repo.create(user)

    def search_users(self, query: str) -> List[User]:
        """
        Search users by username

        Args:
            query: Search query

        Returns:
            List of matching users
        """
        return self.user_repo.search_by_username(query)

    def change_role(
        self,
        mastodon_id: str,
        new_role: str,
        admin_name: str
    ) -> None:
        """
        Change user role with validation

        Args:
            mastodon_id: User's Mastodon ID
            new_role: New role
            admin_name: Admin making the change

        Raises:
            ValueError: If new_role is invalid
        """
        if new_role not in self.VALID_ROLES:
            raise ValueError(f'Invalid role: {new_role}. Must be one of {self.VALID_ROLES}')

        self.user_repo.update_role(mastodon_id, new_role)

        # TODO: Log admin action

    def adjust_balance(
        self,
        user_id: str,
        amount: int,
        transaction_type: str,
        admin_name: str,
        description: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Adjust user balance and create transaction record

        This is the core business logic that ensures atomicity:
        - Balance is adjusted in users table
        - Transaction record is created in transactions table
        - If either fails, both should rollback (handled by repository)

        Args:
            user_id: User's Mastodon ID
            amount: Amount to adjust (positive for credit, negative for debit)
            transaction_type: Type of transaction
            admin_name: Admin making the adjustment
            description: Transaction description (optional)
            category: Transaction category (optional)

        Returns:
            Dictionary with updated user and created transaction

        Raises:
            ValueError: If balance would become negative
        """
        # 1. Adjust balance (this also updates total_earned/total_spent)
        self.user_repo.adjust_balance(user_id, amount)

        # 2. Create transaction record
        transaction = Transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            category=category,
            admin_name=admin_name
        )
        created_transaction = self.transaction_repo.create(transaction)

        # 3. Get updated user
        updated_user = self.user_repo.find_by_id(user_id)

        return {
            'user': updated_user,
            'transaction': created_transaction
        }

    def get_user_statistics(self, user_id: str) -> Dict[str, any]:
        """
        Get comprehensive user statistics

        Args:
            user_id: User's Mastodon ID

        Returns:
            Dictionary with user data and statistics
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f'User not found: {user_id}')

        # Get transaction summary
        transaction_summary = self.transaction_repo.get_user_summary(user_id)

        # Get all transactions for count
        user_transactions = self.transaction_repo.find_by_user(user_id)

        return {
            'user': user,
            'current_balance': user.balance,
            'transaction_count': len(user_transactions),
            'total_credit': transaction_summary['total_credit'],
            'total_debit': transaction_summary['total_debit'],
            'net_amount': transaction_summary['net_amount']
        }

    def add_warning(self, mastodon_id: str, admin_name: str) -> None:
        """
        Increment user warning count

        Args:
            mastodon_id: User's Mastodon ID
            admin_name: Admin issuing the warning
        """
        self.user_repo.increment_warning_count(mastodon_id)

        # TODO: Log admin action
        # TODO: Check if user should be auto-banned (warning_count >= 3)

    def set_key_member(
        self,
        mastodon_id: str,
        is_key_member: bool,
        admin_name: str
    ) -> None:
        """
        Set user's key member status

        Args:
            mastodon_id: User's Mastodon ID
            is_key_member: Key member flag
            admin_name: Admin making the change
        """
        self.user_repo.update_key_member(mastodon_id, is_key_member)

        # TODO: Log admin action
