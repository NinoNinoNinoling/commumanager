"""
User Repository
유저 데이터베이스 접근을 담당
"""
import sqlite3
from typing import Optional, List, Dict, Any


class UserRepository:
    """유저 데이터 접근 객체"""

    def __init__(self, db_path: str):
        """
        Args:
            db_path: SQLite 데이터베이스 경로
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결 반환"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_user_by_mastodon_id(self, mastodon_id: str) -> Optional[Dict[str, Any]]:
        """
        마스토돈 ID로 유저 조회

        Args:
            mastodon_id: 마스토돈 유저 ID

        Returns:
            유저 정보 딕셔너리 또는 None
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM users WHERE mastodon_id = ?",
                (mastodon_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        내부 ID로 유저 조회

        Args:
            user_id: 내부 유저 ID

        Returns:
            유저 정보 딕셔너리 또는 None
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_user(self, mastodon_id: str, username: str, display_name: str,
                   is_admin: bool = False) -> int:
        """
        새 유저 생성

        Args:
            mastodon_id: 마스토돈 유저 ID
            username: 유저명
            display_name: 표시 이름
            is_admin: 관리자 여부

        Returns:
            생성된 유저의 ID
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO users (mastodon_id, username, display_name, is_admin, currency)
                VALUES (?, ?, ?, ?, 0)
                """,
                (mastodon_id, username, display_name, is_admin)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update_user_currency(self, user_id: int, amount: int) -> bool:
        """
        유저 재화 업데이트

        Args:
            user_id: 유저 ID
            amount: 변경할 재화량

        Returns:
            성공 여부
        """
        conn = self._get_connection()
        try:
            conn.execute(
                "UPDATE users SET currency = currency + ? WHERE id = ?",
                (amount, user_id)
            )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        모든 유저 조회 (페이지네이션)

        Args:
            limit: 최대 결과 수
            offset: 건너뛸 결과 수

        Returns:
            유저 정보 리스트
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_user_count(self) -> int:
        """
        전체 유저 수 조회

        Returns:
            유저 수
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) as count FROM users")
            row = cursor.fetchone()
            return row['count'] if row else 0
        finally:
            conn.close()
