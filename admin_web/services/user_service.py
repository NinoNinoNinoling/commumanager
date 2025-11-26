from typing import List, Dict, Any, Optional
from flask import current_app

from admin_web.models.user import User
from admin_web.models.transaction import Transaction
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository
from admin_web.repositories.user_stats_repository import UserStatsRepository
from admin_web.constants import SYSTEM_ROLES
from datetime import datetime

class UserService:
    """
    유저 관리 비즈니스 로직을 위한 Service

    직접적인 DB 접근(SQL)을 하지 않고, Repository를 통해서만 데이터를 조작합니다.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = current_app.config.get('DATABASE_PATH', 'economy.db')
        else:
            self.db_path = db_path
            
        # Repository 초기화
        self.user_repo = UserRepository(self.db_path)
        self.transaction_repo = TransactionRepository(self.db_path)
        self.user_stats_repo = UserStatsRepository(self.db_path)

    def get_user(self, user_id: str) -> Optional[User]:
        """Mastodon ID를 사용하여 유저 상세 정보를 조회합니다."""
        return self.user_repo.find_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """
        전체 유저를 조회합니다 (시스템 계정 제외).
        UserRepository의 find_all_non_system_users 메서드를 사용합니다.
        """
        # 상수를 리스트로 변환하여 전달
        return self.user_repo.find_all_non_system_users(list(SYSTEM_ROLES))

    def update_user_role(self, user_id: str, new_role: str) -> User:
        """유저의 역할을 업데이트합니다."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("유저를 찾을 수 없습니다.")

        allowed_roles = ['user', 'admin', 'moderator']
        if new_role not in allowed_roles:
            raise ValueError(f"유효하지 않은 역할입니다: {new_role}")
        
        self.user_repo.update_role(user_id, new_role)
        return self.user_repo.find_by_id(user_id)
        
    def get_risk_users(self) -> List[Dict]:
        """위험 감지 유저를 조회합니다 (시스템 계정 제외)."""
        return self.user_stats_repo.find_risk_users(list(SYSTEM_ROLES))
        
    def adjust_balance(self, user_id: str, amount: int, transaction_type: str, description: str, admin_name: Optional[str] = None) -> Dict[str, Any]:
        """
        유저 잔액을 조정하고 거래 내역을 기록합니다.
        
        Note: 현재 구조상 Repository가 각각 커밋을 수행하므로, 
        엄격한 트랜잭션 원자성이 보장되지 않습니다. (추후 개선 필요)
        하지만 Service 계층에서 불필요한 DB 연결을 맺는 것은 제거했습니다.
        """
        if not isinstance(amount, int) or amount == 0:
            raise ValueError("유효한 금액(정수)을 입력해야 합니다.")

        # 1. 유저 잔액 업데이트 (Repo 내부에서 커밋됨)
        # 실패 시 여기서 예외 발생하고 중단됨
        self.user_repo.adjust_balance(user_id, amount)

        try:
            # 2. 거래 기록 생성 (Repo 내부에서 커밋됨)
            category = "관리자 조정"
            transaction_obj = Transaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                category=category,
                description=description,
                admin_name=admin_name,
                timestamp=datetime.now()
            )
            created_transaction = self.transaction_repo.create(transaction_obj)

            # 3. 업데이트된 잔액 조회
            updated_user = self.user_repo.find_by_id(user_id)
            new_balance = updated_user.balance if updated_user else 0

            return {
                'status': 'success',
                'user_id': user_id,
                'new_balance': new_balance,
                'transaction_id': created_transaction.id
            }

        except Exception as e:
            # 로그 기록 실패 시에도 잔액은 이미 변경되었음을 인지해야 함
            # (현재 아키텍처의 한계점 주석 처리)
            raise e
