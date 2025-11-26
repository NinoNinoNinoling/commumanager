import sqlite3
from typing import List
from admin_web.models.transaction import Transaction
from admin_web.utils.datetime_utils import parse_datetime

class TransactionRepository:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_transaction(self, row) -> Transaction:
        return Transaction(
            id=row['id'],
            user_id=row['user_id'],
            transaction_type=row['transaction_type'],
            amount=row['amount'],
            category=row['category'],
            description=row['description'],
            admin_name=row['admin_name'],
            timestamp=parse_datetime(row['timestamp'])
        )

    def find_all(self) -> List[Transaction]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_transaction(row) for row in rows]

    def find_by_user(self, user_id: str) -> List[Transaction]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_transaction(row) for row in rows]

    # [수정됨] 외부 커넥션을 받을 수 있도록 connection 인자 추가
    def create(self, transaction: Transaction, connection: sqlite3.Connection = None) -> Transaction:
        should_close = False
        if connection is None:
            conn = self._get_connection()
            should_close = True
        else:
            conn = connection

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (
                    user_id, transaction_type, amount, category, description, admin_name, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.user_id,
                transaction.transaction_type,
                transaction.amount,
                transaction.category,
                transaction.description,
                transaction.admin_name,
                transaction.timestamp
            ))
            
            if should_close:
                conn.commit()
                # ID를 가져오기 위해 커밋 후 조회 필요할 수 있으나 lastrowid 사용
            
            transaction.id = cursor.lastrowid
            return transaction

        except Exception:
            if should_close:
                conn.rollback()
            raise
        finally:
            if should_close:
                conn.close()
