import sqlite3
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
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = current_app.config.get('DATABASE_PATH', 'economy.db')
        else:
            self.db_path = db_path
            
        self.user_repo = UserRepository(self.db_path)
        self.transaction_repo = TransactionRepository(self.db_path)
        self.user_stats_repo = UserStatsRepository(self.db_path)

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repo.find_by_id(user_id)

    def get_all_users(self) -> List[User]:
        return self.user_repo.find_all_non_system_users(list(SYSTEM_ROLES))

    def update_user_role(self, user_id: str, new_role: str) -> User:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("유저를 찾을 수 없습니다.")

        allowed_roles = ['user', 'admin', 'moderator']
        if new_role not in allowed_roles:
            raise ValueError(f"유효하지 않은 역할입니다: {new_role}")
        
        self.user_repo.update_role(user_id, new_role)
        return self.user_repo.find_by_id(user_id)
        
    def get_risk_users(self) -> List[Dict]:
        return self.user_stats_repo.find_risk_users(list(SYSTEM_ROLES))
        
    def adjust_balance(self, user_id: str, amount: int, transaction_type: str, description: str, admin_name: Optional[str] = None) -> Dict[str, Any]:
        """
        유저 잔액을 조정하고 거래 내역을 기록합니다. (원자적 트랜잭션 보장)
        """
        if not isinstance(amount, int) or amount == 0:
            raise ValueError("유효한 금액(정수)을 입력해야 합니다.")

        # [중요] 트랜잭션 시작
        conn = sqlite3.connect(self.db_path)
        try:
            # 1. 유저 잔액 업데이트 (동일한 conn 전달)
            self.user_repo.adjust_balance(user_id, amount, connection=conn)

            # 2. 거래 기록 생성 (동일한 conn 전달)
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
            created_transaction = self.transaction_repo.create(transaction_obj, connection=conn)

            # 3. 모든 작업 성공 시 커밋
            conn.commit()

            # 4. 결과 반환을 위한 데이터 조회 (커밋 후라 안전하게 새 연결 사용 가능하지만, 효율을 위해 그냥 리턴값 구성)
            # (잔액은 쿼리 없이 계산 가능하거나, 필요하면 별도 조회)
            updated_user = self.user_repo.find_by_id(user_id) 
            new_balance = updated_user.balance if updated_user else 0

            return {
                'status': 'success',
                'user_id': user_id,
                'new_balance': new_balance,
                'transaction_id': created_transaction.id
            }

        except Exception as e:
            conn.rollback() # 실패 시 롤백 (잔액 변경 취소됨)
            raise e
        finally:
            conn.close()
