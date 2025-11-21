"""
TransactionRepository

Data access layer for transactions table
"""
import sqlite3
from typing import List, Optional, Dict
from datetime import datetime

from admin_web.models.transaction import Transaction


class TransactionRepository:
    """
    Repository for Transaction data access

    Handles all CRUD operations for transactions table
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        Initialize TransactionRepository

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection with row factory

        Returns:
            SQLite connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_transaction(self, row: sqlite3.Row) -> Transaction:
        """
        Convert database row to Transaction model

        Args:
            row: SQLite row object

        Returns:
            Transaction instance
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
            timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None
        )

    def create(self, transaction: Transaction) -> Transaction:
        """
        Create new transaction

        Args:
            transaction: Transaction instance to create

        Returns:
            Created transaction with ID
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
        Find transaction by ID

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction if found, None otherwise
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
        Find all transactions

        Returns:
            List of all transactions
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
        Find all transactions for a specific user

        Args:
            user_id: User's Mastodon ID

        Returns:
            List of user's transactions
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
        Find transactions by type

        Args:
            transaction_type: Transaction type

        Returns:
            List of transactions with specified type
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
        Find transactions by category

        Args:
            category: Transaction category

        Returns:
            List of transactions with specified category
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
        Count total number of transactions

        Returns:
            Total transaction count
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
        Get transaction summary for a user

        Args:
            user_id: User's Mastodon ID

        Returns:
            Dictionary with total_credit, total_debit, net_amount
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
