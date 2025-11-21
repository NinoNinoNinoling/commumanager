"""
UserService

사용자 관리를 위한 비즈니스 로직 계층
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from admin_web.models.user import User
from admin_web.models.transaction import Transaction
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository


class UserService:
    """
    사용자 관리 비즈니스 로직을 위한 Service

    처리 내용:
    - User CRUD 작업
    - 검증을 포함한 역할 관리
    - 거래 생성을 포함한 잔액 조정
    - 사용자 통계
    """

    VALID_ROLES = {'user', 'admin', 'moderator'}

    def __init__(self, db_path: str = 'economy.db'):
        """
        UserService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.user_repo = UserRepository(db_path)
        self.transaction_repo = TransactionRepository(db_path)
        self.db_path = db_path

    def get_user(self, mastodon_id: str) -> Optional[User]:
        """
        Mastodon ID로 유저를 조회합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID

        Returns:
            찾은 경우 User, 아니면 None
        """
        return self.user_repo.find_by_id(mastodon_id)

    def get_all_users(self) -> List[User]:
        """
        모든 유저를 조회합니다.

        Returns:
            모든 유저의 리스트
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
        새 유저를 생성합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            username: 유저명
            display_name: 표시 이름 (선택)
            role: 유저 역할 (기본값: 'user')

        Returns:
            생성된 유저

        Raises:
            ValueError: 역할이 유효하지 않은 경우
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
        유저명으로 유저를 검색합니다.

        Args:
            query: 검색 쿼리

        Returns:
            일치하는 유저의 리스트
        """
        return self.user_repo.search_by_username(query)

    def change_role(
        self,
        mastodon_id: str,
        new_role: str,
        admin_name: str
    ) -> None:
        """
        검증을 포함하여 유저 역할을 변경합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            new_role: 새 역할
            admin_name: 변경을 수행하는 관리자

        Raises:
            ValueError: new_role이 유효하지 않은 경우
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
    ) -> Dict[str, Any]:
        """
        유저 잔액을 조정하고 거래 기록을 생성합니다.

        원자성을 보장하는 핵심 비즈니스 로직:
        - users 테이블에서 잔액 조정
        - transactions 테이블에 거래 기록 생성
        - 둘 중 하나라도 실패하면 모두 롤백 (repository에서 처리)

        Args:
            user_id: 유저의 Mastodon ID
            amount: 조정할 금액 (양수: 입금, 음수: 출금)
            transaction_type: 거래 유형
            admin_name: 조정을 수행하는 관리자
            description: 거래 설명 (선택)
            category: 거래 카테고리 (선택)

        Returns:
            업데이트된 유저와 생성된 거래를 담은 딕셔너리

        Raises:
            ValueError: 잔액이 음수가 되는 경우
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

    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        포괄적인 유저 통계를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저 데이터와 통계를 담은 딕셔너리
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
        유저 경고 횟수를 증가시킵니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            admin_name: 경고를 발행하는 관리자
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
        유저의 주요 멤버 상태를 설정합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            is_key_member: 주요 멤버 플래그
            admin_name: 변경을 수행하는 관리자
        """
        self.user_repo.update_key_member(mastodon_id, is_key_member)

        # TODO: Log admin action
