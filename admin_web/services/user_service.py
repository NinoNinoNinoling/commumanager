"""User service"""
from typing import List, Optional
from admin_web.models.user import User
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository


class UserService:
    """유저 비즈니스 로직"""

    def __init__(self):
        self.user_repo = UserRepository()
        self.transaction_repo = TransactionRepository()

    def get_user(self, mastodon_id: str) -> Optional[User]:
        """유저 조회"""
        return self.user_repo.find_by_id(mastodon_id)

    def get_users(self, page: int = 1, limit: int = 50, search: str = None,
                  role: str = None, sort: str = 'created_desc') -> dict:
        """유저 목록 조회"""
        users, total = self.user_repo.find_all(page, limit, search, role, sort)
        total_pages = (total + limit - 1) // limit

        return {
            'users': [u.to_dict() for u in users],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }

    def get_user_detail(self, mastodon_id: str) -> Optional[dict]:
        """유저 상세 정보"""
        user = self.user_repo.find_by_id(mastodon_id)
        if not user:
            return None

        # 48시간 활동량 조회 (PostgreSQL)
        activity_48h = self.user_repo.get_activity_48h(mastodon_id)

        detail = user.to_dict()
        detail['activity_48h'] = activity_48h
        detail['is_on_vacation'] = False  # TODO: vacation 체크
        detail['warning_count'] = 0  # TODO: warning 카운트

        return detail

    def change_role(self, mastodon_id: str, new_role: str) -> bool:
        """역할 변경"""
        if new_role not in ['user', 'admin']:
            raise ValueError("Invalid role")

        return self.user_repo.update_role(mastodon_id, new_role)

    def adjust_balance(self, mastodon_id: str, amount: int, description: str, admin_name: str) -> bool:
        """재화 조정"""
        # 1. 재화 업데이트
        success = self.user_repo.update_balance(mastodon_id, amount)
        if not success:
            return False

        # 2. 거래 내역 생성
        from admin_web.models.transaction import Transaction
        transaction = Transaction(
            id=None,
            user_id=mastodon_id,
            transaction_type='admin_adjust',
            amount=amount,
            description=description,
            admin_name=admin_name,
        )
        self.transaction_repo.create(transaction)

        return True
