"""
WarningRepository

warnings 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.warning import Warning
from admin_web.utils.datetime_utils import parse_datetime


class WarningRepository:
    """
    Warning 데이터 접근을 위한 Repository

    warnings 테이블에 대한 모든 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        WarningRepository를 초기화합니다.

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

    def _row_to_warning(self, row: sqlite3.Row) -> Warning:
        """
        데이터베이스 row를 Warning 모델로 변환합니다.

        Args:
            row: SQLite row 객체

        Returns:
            Warning 인스턴스
        """
        return Warning(
            id=row['id'],
            user_id=row['user_id'],
            warning_type=row['warning_type'],
            check_period_hours=row['check_period_hours'],
            required_replies=row['required_replies'],
            actual_replies=row['actual_replies'],
            message=row['message'],
            dm_sent=bool(row['dm_sent']),
            admin_name=row['admin_name'],
            timestamp=parse_datetime(row['timestamp'])
        )

    def create(self, warning: Warning, connection=None) -> Warning:
        """
        새 경고를 생성합니다.

        Args:
            warning: 생성할 Warning 인스턴스
            connection: 트랜잭션용 연결 (선택사항)

        Returns:
            ID가 포함된 생성된 경고
        """
        conn = connection or self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO warnings (
                user_id, warning_type,
                check_period_hours, required_replies, actual_replies,
                message, dm_sent, admin_name, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            warning.user_id,
            warning.warning_type,
            warning.check_period_hours,
            warning.required_replies,
            warning.actual_replies,
            warning.message,
            1 if warning.dm_sent else 0,
            warning.admin_name
        ))

        warning_id = cursor.lastrowid

        if connection is None:  # 독립 호출이면 자동 커밋
            conn.commit()
            conn.close()

        return self.find_by_id(warning_id)

    def find_by_id(self, warning_id: int) -> Optional[Warning]:
        """
        ID로 경고를 조회합니다.

        Args:
            warning_id: 경고 ID

        Returns:
            찾은 경우 Warning, 아니면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM warnings
            WHERE id = ?
        """, (warning_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_warning(row)
        return None

    def find_all(self) -> List[Warning]:
        """
        모든 경고를 조회합니다.

        Returns:
            모든 경고의 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM warnings
            ORDER BY timestamp DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_warning(row) for row in rows]

    def find_by_user(self, user_id: str) -> List[Warning]:
        """
        특정 유저의 모든 경고를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저의 경고 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM warnings
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_warning(row) for row in rows]

    def find_by_type(self, warning_type: str) -> List[Warning]:
        """
        유형별로 경고를 조회합니다.

        Args:
            warning_type: 경고 유형

        Returns:
            지정된 유형의 경고 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM warnings
            WHERE warning_type = ?
            ORDER BY timestamp DESC
        """, (warning_type,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_warning(row) for row in rows]

    def count(self) -> int:
        """
        전체 경고 수를 계산합니다.

        Returns:
            전체 경고 개수
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM warnings
        """)

        row = cursor.fetchone()
        conn.close()

        return row['count']

    def get_user_warning_count(self, user_id: str) -> int:
        """
        특정 유저의 경고 수를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저의 경고 개수
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM warnings
            WHERE user_id = ?
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        return row['count']

    def update_dm_sent(self, warning_id: int, dm_sent: bool) -> None:
        """
        경고의 DM 전송 상태를 업데이트합니다.

        Args:
            warning_id: 경고 ID
            dm_sent: DM 전송 여부
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE warnings
            SET dm_sent = ?
            WHERE id = ?
        """, (1 if dm_sent else 0, warning_id))

        conn.commit()
        conn.close()
