"""
UserRepository

Data access layer for users table
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.user import User


class UserRepository:
    """
    Repository for User data access

    Handles all CRUD operations for users table
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        Initialize UserRepository

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

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """
        Convert database row to User model

        Args:
            row: SQLite row object

        Returns:
            User instance
        """
        return User(
            mastodon_id=row['mastodon_id'],
            username=row['username'],
            display_name=row['display_name'],
            role=row['role'],
            dormitory=row['dormitory'],
            balance=row['balance'],
            total_earned=row['total_earned'],
            total_spent=row['total_spent'],
            reply_count=row['reply_count'],
            warning_count=row['warning_count'],
            is_key_member=bool(row['is_key_member']),
            last_active=datetime.fromisoformat(row['last_active']) if row['last_active'] else None,
            last_check=datetime.fromisoformat(row['last_check']) if row['last_check'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def find_by_id(self, mastodon_id: str) -> Optional[User]:
        """
        Find user by mastodon ID

        Args:
            mastodon_id: User's Mastodon ID

        Returns:
            User if found, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE mastodon_id = ?
        """, (mastodon_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_user(row)
        return None

    def find_all(self) -> List[User]:
        """
        Find all users

        Returns:
            List of all users
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_user(row) for row in rows]

    def find_by_role(self, role: str) -> List[User]:
        """
        Find users by role

        Args:
            role: User role (user, admin, moderator)

        Returns:
            List of users with specified role
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE role = ?
            ORDER BY username
        """, (role,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_user(row) for row in rows]

    def search_by_username(self, query: str) -> List[User]:
        """
        Search users by username (partial match)

        Args:
            query: Search query

        Returns:
            List of matching users
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE username LIKE ?
            ORDER BY username
        """, (f'%{query}%',))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_user(row) for row in rows]

    def create(self, user: User) -> User:
        """
        Create new user

        Args:
            user: User instance to create

        Returns:
            Created user

        Raises:
            sqlite3.IntegrityError: If user with same mastodon_id already exists
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (
                mastodon_id, username, display_name, role, dormitory,
                balance, total_earned, total_spent, reply_count,
                warning_count, is_key_member,
                last_active, last_check, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            user.mastodon_id,
            user.username,
            user.display_name,
            user.role,
            user.dormitory,
            user.balance,
            user.total_earned,
            user.total_spent,
            user.reply_count,
            user.warning_count,
            1 if user.is_key_member else 0,
            user.last_active.isoformat() if user.last_active else None,
            user.last_check.isoformat() if user.last_check else None
        ))

        conn.commit()
        conn.close()

        return self.find_by_id(user.mastodon_id)

    def update_balance(self, mastodon_id: str, new_balance: int) -> None:
        """
        Update user balance

        Args:
            mastodon_id: User's Mastodon ID
            new_balance: New balance value
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET balance = ?
            WHERE mastodon_id = ?
        """, (new_balance, mastodon_id))

        conn.commit()
        conn.close()

    def adjust_balance(self, mastodon_id: str, amount: int) -> None:
        """
        Adjust user balance and update total_earned or total_spent

        Args:
            mastodon_id: User's Mastodon ID
            amount: Amount to adjust (positive for credit, negative for debit)

        Raises:
            ValueError: If balance would become negative
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get current balance
        cursor.execute("""
            SELECT balance FROM users
            WHERE mastodon_id = ?
        """, (mastodon_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f'User not found: {mastodon_id}')

        current_balance = row['balance']
        new_balance = current_balance + amount

        # Check for negative balance
        if new_balance < 0:
            conn.close()
            raise ValueError('Insufficient balance')

        # Update balance and totals
        if amount > 0:
            # Credit: increase total_earned
            cursor.execute("""
                UPDATE users
                SET balance = balance + ?,
                    total_earned = total_earned + ?
                WHERE mastodon_id = ?
            """, (amount, amount, mastodon_id))
        else:
            # Debit: increase total_spent
            cursor.execute("""
                UPDATE users
                SET balance = balance + ?,
                    total_spent = total_spent + ?
                WHERE mastodon_id = ?
            """, (amount, abs(amount), mastodon_id))

        conn.commit()
        conn.close()

    def update_role(self, mastodon_id: str, role: str) -> None:
        """
        Update user role

        Args:
            mastodon_id: User's Mastodon ID
            role: New role
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET role = ?
            WHERE mastodon_id = ?
        """, (role, mastodon_id))

        conn.commit()
        conn.close()

    def increment_warning_count(self, mastodon_id: str) -> None:
        """
        Increment user warning count by 1

        Args:
            mastodon_id: User's Mastodon ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET warning_count = warning_count + 1
            WHERE mastodon_id = ?
        """, (mastodon_id,))

        conn.commit()
        conn.close()

    def update_key_member(self, mastodon_id: str, is_key_member: bool) -> None:
        """
        Update key member flag

        Args:
            mastodon_id: User's Mastodon ID
            is_key_member: Key member flag
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET is_key_member = ?
            WHERE mastodon_id = ?
        """, (1 if is_key_member else 0, mastodon_id))

        conn.commit()
        conn.close()
