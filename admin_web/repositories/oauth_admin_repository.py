"""
OAuthAdminRepository

oauth_admins 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.oauth_admin import OAuthAdmin


class OAuthAdminRepository:
    """
    OAuth 관리자 데이터 접근을 위한 Repository

    oauth_admins 테이블에 대한 모든 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        OAuthAdminRepository를 초기화합니다.

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

    def _row_to_oauth_admin(self, row: sqlite3.Row) -> OAuthAdmin:
        """
        데이터베이스 row를 OAuthAdmin 모델로 변환합니다.

        Args:
            row: SQLite row 객체

        Returns:
            OAuthAdmin 인스턴스
        """
        return OAuthAdmin(
            id=row['id'],
            mastodon_acct=row['mastodon_acct'],
            display_name=row['display_name'],
            added_by=row['added_by'],
            added_at=datetime.fromisoformat(row['added_at']) if row['added_at'] else None,
            is_active=bool(row['is_active']),
            last_login_at=datetime.fromisoformat(row['last_login_at']) if row['last_login_at'] else None
        )

    def find_by_acct(self, mastodon_acct: str) -> Optional[OAuthAdmin]:
        """
        Mastodon 계정으로 관리자를 조회합니다.

        Args:
            mastodon_acct: Mastodon 계정 (예: 'admin', 'user@remote.instance')

        Returns:
            찾은 경우 OAuthAdmin, 아니면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM oauth_admins
            WHERE mastodon_acct = ?
        """, (mastodon_acct,))

        row = cursor.fetchone()
        conn.close()

        return self._row_to_oauth_admin(row) if row else None

    def is_admin(self, mastodon_acct: str) -> bool:
        """
        주어진 계정이 활성화된 관리자인지 확인합니다.

        Args:
            mastodon_acct: Mastodon 계정

        Returns:
            활성화된 관리자이면 True, 아니면 False
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM oauth_admins
            WHERE mastodon_acct = ? AND is_active = 1
        """, (mastodon_acct,))

        row = cursor.fetchone()
        conn.close()

        return row['count'] > 0 if row else False

    def find_all(self) -> List[OAuthAdmin]:
        """
        모든 OAuth 관리자를 조회합니다.

        Returns:
            OAuthAdmin 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM oauth_admins
            ORDER BY added_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_oauth_admin(row) for row in rows]

    def find_active(self) -> List[OAuthAdmin]:
        """
        활성화된 OAuth 관리자만 조회합니다.

        Returns:
            활성화된 OAuthAdmin 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM oauth_admins
            WHERE is_active = 1
            ORDER BY added_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_oauth_admin(row) for row in rows]

    def create(self, admin: OAuthAdmin) -> OAuthAdmin:
        """
        새로운 OAuth 관리자를 생성합니다.

        Args:
            admin: 생성할 OAuthAdmin 객체

        Returns:
            생성된 OAuthAdmin (ID 포함)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO oauth_admins (mastodon_acct, display_name, added_by, is_active)
            VALUES (?, ?, ?, ?)
        """, (
            admin.mastodon_acct,
            admin.display_name,
            admin.added_by,
            1 if admin.is_active else 0
        ))

        admin.id = cursor.lastrowid
        conn.commit()
        conn.close()

        return admin

    def update_last_login(self, mastodon_acct: str, login_time: datetime) -> bool:
        """
        마지막 로그인 시각을 업데이트합니다.

        Args:
            mastodon_acct: Mastodon 계정
            login_time: 로그인 시각

        Returns:
            업데이트 성공 여부
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE oauth_admins
            SET last_login_at = ?
            WHERE mastodon_acct = ?
        """, (login_time.isoformat(), mastodon_acct))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

    def deactivate(self, mastodon_acct: str) -> bool:
        """
        관리자를 비활성화합니다.

        Args:
            mastodon_acct: Mastodon 계정

        Returns:
            비활성화 성공 여부
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE oauth_admins
            SET is_active = 0
            WHERE mastodon_acct = ?
        """, (mastodon_acct,))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

    def activate(self, mastodon_acct: str) -> bool:
        """
        관리자를 활성화합니다.

        Args:
            mastodon_acct: Mastodon 계정

        Returns:
            활성화 성공 여부
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE oauth_admins
            SET is_active = 1
            WHERE mastodon_acct = ?
        """, (mastodon_acct,))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

    def delete(self, mastodon_acct: str) -> bool:
        """
        관리자를 삭제합니다.

        Args:
            mastodon_acct: Mastodon 계정

        Returns:
            삭제 성공 여부
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM oauth_admins
            WHERE mastodon_acct = ?
        """, (mastodon_acct,))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0
