"""
BanRecordRepository

ban_records 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.ban_record import BanRecord


class BanRecordRepository:
    """
    BanRecord 데이터 접근을 위한 Repository

    ban_records 테이블에 대한 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        BanRecordRepository를 초기화합니다.

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

    def _row_to_ban_record(self, row: sqlite3.Row) -> BanRecord:
        """
        데이터베이스 row를 BanRecord 모델로 변환합니다.

        Args:
            row: SQLite row 객체

        Returns:
            BanRecord 인스턴스
        """
        return BanRecord(
            id=row['id'],
            user_id=row['user_id'],
            banned_at=datetime.fromisoformat(row['banned_at']) if row['banned_at'] else None,
            banned_by=row['banned_by'],
            reason=row['reason'],
            warning_count=row['warning_count'],
            evidence_snapshot=row['evidence_snapshot'],
            is_active=bool(row['is_active']),
            unbanned_at=datetime.fromisoformat(row['unbanned_at']) if row['unbanned_at'] else None,
            unbanned_by=row['unbanned_by'],
            unban_reason=row['unban_reason']
        )

    def create(self, ban_record: BanRecord) -> BanRecord:
        """
        새 아웃 기록을 생성합니다.

        Args:
            ban_record: 생성할 BanRecord 인스턴스

        Returns:
            ID가 포함된 생성된 아웃 기록
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ban_records (
                user_id, banned_by, reason, warning_count,
                evidence_snapshot, is_active
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ban_record.user_id,
            ban_record.banned_by,
            ban_record.reason,
            ban_record.warning_count,
            ban_record.evidence_snapshot,
            1 if ban_record.is_active else 0
        ))

        ban_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return self.find_by_id(ban_id)

    def find_by_id(self, ban_id: int) -> Optional[BanRecord]:
        """
        ID로 아웃 기록을 조회합니다.

        Args:
            ban_id: 아웃 기록 ID

        Returns:
            찾은 경우 BanRecord, 아니면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM ban_records
            WHERE id = ?
        """, (ban_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_ban_record(row)
        return None

    def find_by_user(self, user_id: str) -> List[BanRecord]:
        """
        특정 유저의 모든 아웃 기록을 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저의 아웃 기록 리스트 (시간 역순)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM ban_records
            WHERE user_id = ?
            ORDER BY banned_at DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_ban_record(row) for row in rows]

    def find_active_ban(self, user_id: str) -> Optional[BanRecord]:
        """
        유저의 활성 아웃 기록을 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            활성 아웃 기록, 없으면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM ban_records
            WHERE user_id = ? AND is_active = 1
            ORDER BY banned_at DESC
            LIMIT 1
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_ban_record(row)
        return None
