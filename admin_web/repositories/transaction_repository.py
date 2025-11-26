"""
TransactionRepository

transactions 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional, Dict
from datetime import datetime

from admin_web.models.transaction import Transaction
from admin_web.utils.datetime_utils import parse_datetime


class TransactionRepository:
    """
    Transaction 데이터 접근을 위한 Repository

    transactions 테이블에 대한 모든 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        TransactionRepository를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """
        Row factory가 설정된 데이터베이스 연결을 가져옵니다.

        Returns:
            SQLite 연결 객체
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_transaction(self, row: sqlite3.Row) -> Transaction:
        """
        데이터베이스 row를 Transaction 모델로 변환합니다.

        Args:
            row: SQLite row 객체

        Returns:
            Transaction 인스턴스
        """
        return Transaction(
            id=row['id'],
            user_id=row['user_id'],
            transaction_type=row['transaction_type'],
            amount=row['amount'],
            status_id=row['status_id'],
            item_id=row['item_id'],
            category=row['category'],
            description=row['description'],
            admin_name=row['admin_name'],
            timestamp=parse_datetime(row['timestamp'])
        )

    def create(self, transaction: Transaction) -> Transaction:
        """
        새 거래를 생성합니다.

        Args:
            transaction: 생성할 Transaction 인스턴스

        Returns:
            ID가 포함된 생성된 거래
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transactions (
                user_id, transaction_type, amount,
                status_id, item_id, category, description,
                admin_name, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            transaction.user_id,
            transaction.transaction_type,
            transaction.amount,
            transaction.status_id,
            transaction.item_id,
            transaction.category,
            transaction.description,
            transaction.admin_name
        ))

        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return self.find_by_id(transaction_id)

    def find_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        ID로 거래를 조회합니다.

        Args:
            transaction_id: 거래 ID

        Returns:
            찾은 경우 Transaction, 아니면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM transactions
            WHERE id = ?
        """, (transaction_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_transaction(row)
        return None

    def find_all(self) -> List[Transaction]:
        """
        모든 거래를 조회합니다.

        Returns:
            모든 거래의 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM transactions
            ORDER BY timestamp DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_transaction(row) for row in rows]

    def find_by_user(self, user_id: str) -> List[Transaction]:
        """
        특정 유저의 모든 거래를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저의 거래 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM transactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_transaction(row) for row in rows]

    def find_by_type(self, transaction_type: str) -> List[Transaction]:
        """
        유형별로 거래를 조회합니다.

        Args:
            transaction_type: 거래 유형

        Returns:
            지정된 유형의 거래 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM transactions
            WHERE transaction_type = ?
            ORDER BY timestamp DESC
        """, (transaction_type,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_transaction(row) for row in rows]

    def find_by_category(self, category: str) -> List[Transaction]:
        """
        카테고리별로 거래를 조회합니다.

        Args:
            category: 거래 카테고리

        Returns:
            지정된 카테고리의 거래 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM transactions
            WHERE category = ?
            ORDER BY timestamp DESC
        """, (category,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_transaction(row) for row in rows]

    def count(self) -> int:
        """
        전체 거래 수를 계산합니다.

        Returns:
            전체 거래 개수
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM transactions
        """)

        row = cursor.fetchone()
        conn.close()

        return row['count']

    def get_user_summary(self, user_id: str) -> Dict[str, int]:
        """
        유저의 거래 요약을 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            total_credit, total_debit, net_amount를 담은 딕셔너리
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Calculate total credit (positive amounts)
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total_credit
            FROM transactions
            WHERE user_id = ? AND amount > 0
        """, (user_id,))
        total_credit = cursor.fetchone()['total_credit']

        # Calculate total debit (negative amounts, as absolute value)
        cursor.execute("""
            SELECT COALESCE(SUM(ABS(amount)), 0) as total_debit
            FROM transactions
            WHERE user_id = ? AND amount < 0
        """, (user_id,))
        total_debit = cursor.fetchone()['total_debit']

        conn.close()

        return {
            'total_credit': total_credit,
            'total_debit': total_debit,
            'net_amount': total_credit - total_debit
        }
