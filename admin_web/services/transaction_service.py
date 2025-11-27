"""
TransactionService

거래 내역 조회 및 통계 계산을 위한 비즈니스 로직
"""
import sqlite3
from typing import List, Dict, Any
from admin_web.repositories.transaction_repository import TransactionRepository
from admin_web.repositories.user_repository import UserRepository


class TransactionService:
    """
    Transaction 비즈니스 로직을 위한 Service

    거래 내역 조회, 유저별 통계 계산 등의 기능을 제공합니다.
    TransactionRepository와 UserRepository를 사용하여 DB에 접근합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        TransactionService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.transaction_repo = TransactionRepository(db_path)
        self.user_repo = UserRepository(db_path)

    def get_user_transactions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        특정 유저의 거래 내역을 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID
            limit: 조회할 최대 거래 수 (기본값: 50)
            offset: 건너뛸 거래 수 (페이지네이션용, 기본값: 0)

        Returns:
            거래 내역 리스트 (최신순)
        """
        transactions = self.transaction_repo.find_by_user(user_id)

        # offset과 limit 적용
        start = offset
        end = offset + limit
        limited_transactions = transactions[start:end]

        return [t.to_dict() for t in limited_transactions]

    def get_transaction_stats(self, user_id: str) -> Dict[str, int]:
        """
        유저의 거래 통계(누적 획득/사용량)를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            total_earned, total_spent를 담은 딕셔너리
        """
        user = self.user_repo.find_by_id(user_id)

        if user:
            return {
                'total_earned': user.total_earned,
                'total_spent': user.total_spent
            }
        return {'total_earned': 0, 'total_spent': 0}

    def delete_transaction(self, transaction_id: int) -> Dict[str, Any]:
        """
        거래 내역을 삭제하고 유저의 잔액을 복원합니다. (원자적 트랜잭션)

        Args:
            transaction_id: 삭제할 거래 ID

        Returns:
            삭제 결과 딕셔너리

        Raises:
            ValueError: 거래 내역이 존재하지 않는 경우
        """
        # 거래 내역 조회 (트랜잭션 외부)
        transaction = self.transaction_repo.find_by_id(transaction_id)
        if not transaction:
            raise ValueError('Transaction not found')

        user_id = transaction.user_id
        amount = transaction.amount  # 원래 거래 금액

        # [중요] 원자적 트랜잭션: Transaction 삭제 + User 잔액 복원
        conn = sqlite3.connect(self.db_path)
        try:
            # 1. Transaction 삭제
            deleted = self.transaction_repo.delete(transaction_id, connection=conn)

            # 2. User 잔액 복원 (거래를 취소하므로 반대로 조정)
            # 예: 원래 -100 (지출)이었다면, +100으로 복원
            self.user_repo.adjust_balance(user_id, -amount, connection=conn)

            # 3. 모든 작업 성공 시 커밋
            conn.commit()

            # 4. 업데이트된 유저 정보 조회
            updated_user = self.user_repo.find_by_id(user_id)

            return {
                'success': True,
                'deleted_transaction_id': transaction_id,
                'refunded_amount': -amount,
                'user': updated_user.to_dict() if updated_user else None
            }

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
