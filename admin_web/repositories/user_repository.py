"""
UserRepository

users 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.user import User
from admin_web.utils.datetime_utils import parse_datetime


class UserRepository:
    """
    User 데이터 접근을 위한 Repository
    """

    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_user(self, row: sqlite3.Row) -> User:
        created_at_val = row['created_at'] if 'created_at' in row.keys() else None
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
            created_at=parse_datetime(created_at_val),
            role_name=row['role_name'],
            role_color=row['role_color']
        )

    def find_by_id(self, mastodon_id: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE mastodon_id = ?", (mastodon_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._row_to_user(row)
        return None

    def find_all(self) -> List[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_user(row) for row in rows]

    def find_all_non_system_users(self, system_roles: List[str]) -> List[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if not system_roles:
                return self.find_all()
            placeholders = ','.join(['?'] * len(system_roles))
            sql = f"SELECT * FROM users WHERE role_name IS NULL OR role_name NOT IN ({placeholders}) ORDER BY created_at DESC"
            cursor.execute(sql, system_roles)
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]
        finally:
            conn.close()

    def create(self, user: User) -> User:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (
                mastodon_id, username, display_name, role, dormitory,
                balance, total_earned, total_spent, reply_count,
                warning_count, is_key_member,
                last_active, last_check, created_at,
                role_name, role_color
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
        """, (
            user.mastodon_id, user.username, user.display_name, user.role, user.dormitory,
            user.balance, user.total_earned, user.total_spent, user.reply_count,
            user.warning_count, 1 if user.is_key_member else 0,
            user.last_active.isoformat() if user.last_active else None,
            user.last_check.isoformat() if user.last_check else None,
            user.role_name, user.role_color
        ))
        conn.commit()
        conn.close()
        return self.find_by_id(user.mastodon_id)

    def update_role(self, mastodon_id: str, role: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE mastodon_id = ?", (role, mastodon_id))
        conn.commit()
        conn.close()

    def increment_warning_count(self, mastodon_id: str, connection=None) -> None:
        """
        유저의 경고 횟수를 1 증가시킵니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            connection: 트랜잭션용 연결 (선택사항)
        """
        conn = connection or self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET warning_count = warning_count + 1 WHERE mastodon_id = ?", (mastodon_id,))

        if connection is None:  # 독립 호출이면 자동 커밋
            conn.commit()
            conn.close()

    def update_key_member(self, mastodon_id: str, is_key_member: bool) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_key_member = ? WHERE mastodon_id = ?", (1 if is_key_member else 0, mastodon_id))
        conn.commit()
        conn.close()

    # [수정됨] 외부 커넥션을 받을 수 있도록 connection 인자 추가
    def adjust_balance(self, mastodon_id: str, amount: int, connection: sqlite3.Connection = None) -> None:
        """
        유저 잔액을 조정합니다. connection이 주어지면 해당 트랜잭션 내에서 실행됩니다.
        """
        should_close = False
        if connection is None:
            conn = self._get_connection()
            should_close = True
        else:
            conn = connection

        try:
            cursor = conn.cursor()
            
            # 현재 잔액 확인
            cursor.execute("SELECT balance FROM users WHERE mastodon_id = ?", (mastodon_id,))
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f'User not found: {mastodon_id}')

            current_balance = row['balance']
            new_balance = current_balance + amount

            if new_balance < 0:
                raise ValueError('Insufficient balance')

            if amount > 0:
                cursor.execute("""
                    UPDATE users SET balance = balance + ?, total_earned = total_earned + ? WHERE mastodon_id = ?
                """, (amount, amount, mastodon_id))
            else:
                cursor.execute("""
                    UPDATE users SET balance = balance + ?, total_spent = total_spent + ? WHERE mastodon_id = ?
                """, (amount, abs(amount), mastodon_id))
            
            # 외부 커넥션이 아닐 때만 여기서 커밋
            if should_close:
                conn.commit()
                
        except Exception:
            if should_close:
                conn.rollback()
            raise
        finally:
            if should_close:
                conn.close()
