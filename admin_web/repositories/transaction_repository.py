"""Transaction repository"""
from typing import List, Optional
from admin_web.models.transaction import Transaction
from admin_web.repositories.database import get_economy_db


class TransactionRepository:
    """거래 내역 저장소"""

    @staticmethod
    def find_by_user(user_id: str, page: int = 1, limit: int = 50,
                     transaction_type: str = None) -> tuple[List[Transaction], int]:
        """유저별 거래 내역 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            conditions = ["user_id = ?"]
            params = [user_id]

            if transaction_type:
                conditions.append("transaction_type = ?")
                params.append(transaction_type)

            where_clause = " AND ".join(conditions)

            # 전체 개수
            cursor.execute(f"SELECT COUNT(*) FROM transactions WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT * FROM transactions
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])

            transactions = [Transaction(**dict(row)) for row in cursor.fetchall()]
            return transactions, total

    @staticmethod
    def create(transaction: Transaction) -> Transaction:
        """거래 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions
                (user_id, transaction_type, amount, status_id, item_id, description, admin_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (transaction.user_id, transaction.transaction_type, transaction.amount,
                  transaction.status_id, transaction.item_id, transaction.description,
                  transaction.admin_name))
            conn.commit()
            transaction.id = cursor.lastrowid
            return transaction

    @staticmethod
    def get_total_earned() -> int:
        """전체 획득 재화"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(total_earned) FROM users")
            result = cursor.fetchone()[0]
            return result or 0

    @staticmethod
    def get_total_spent() -> int:
        """전체 사용 재화"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(total_spent) FROM users")
            result = cursor.fetchone()[0]
            return result or 0
