"""
UserRepository

users 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import datetime # Import datetime

from admin_web.models.user import User
from admin_web.utils.datetime_utils import parse_datetime


class UserRepository:
    """
    User 데이터 접근을 위한 Repository

    users 테이블에 대한 모든 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        UserRepository를 초기화합니다.

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

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """
        데이터베이스 row를 User 모델로 변환합니다.

        Args:
            row: SQLite row 객체

        Returns:
            User 인스턴스
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
            last_active=parse_datetime(row['last_active']),
            last_check=parse_datetime(row['last_check']),
            role_name=row['role_name'],
            role_color=row['role_color']
        )

    def find_by_id(self, mastodon_id: str) -> Optional[User]:
        """
        Mastodon ID로 유저를 조회합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID

        Returns:
            찾은 경우 User, 아니면 None
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
        모든 유저를 조회합니다.

        Returns:
            모든 유저의 리스트
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
        역할별로 유저를 조회합니다.

        Args:
            role: 유저 역할 (user, admin, moderator)

        Returns:
            지정된 역할을 가진 유저의 리스트
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
        유저명으로 유저를 검색합니다 (부분 일치).

        Args:
            query: 검색 쿼리

        Returns:
            일치하는 유저의 리스트
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
        새 유저를 생성합니다.

        Args:
            user: 생성할 User 인스턴스

        Returns:
            생성된 유저

        Raises:
            sqlite3.IntegrityError: 동일한 mastodon_id를 가진 유저가 이미 존재하는 경우
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (
                mastodon_id, username, display_name, role, dormitory,
                balance, total_earned, total_spent, reply_count,
                warning_count, is_key_member,
                last_active, last_check, 
                role_name, role_color
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            user.last_check.isoformat() if user.last_check else None,
            user.role_name,
            user.role_color
        ))

        conn.commit()
        conn.close()

        return self.find_by_id(user.mastodon_id)

    def update_balance(self, mastodon_id: str, new_balance: int) -> None:
        """
        유저 잔액을 업데이트합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            new_balance: 새 잔액 값
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
        유저 잔액을 조정하고 total_earned 또는 total_spent를 업데이트합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            amount: 조정할 금액 (양수: 입금, 음수: 출금)

        Raises:
            ValueError: 잔액이 음수가 되는 경우
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
        유저 역할을 업데이트합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            role: 새 역할
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
        유저 경고 횟수를 1 증가시킵니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
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
        주요 멤버 플래그를 업데이트합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            is_key_member: 주요 멤버 플래그
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

    def update_role_info(self, mastodon_id: str, role_name: Optional[str] = None,
                        role_color: Optional[str] = None) -> None:
        """
        마스토돈 역할 정보를 업데이트합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            role_name: 마스토돈 역할 이름 (Owner, Admin, 봇 등)
            role_color: 마스토돈 역할 색상 (#ff3838 등)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET role_name = ?, role_color = ?
            WHERE mastodon_id = ?
        """, (role_name, role_color, mastodon_id))

        conn.commit()
        conn.close()
