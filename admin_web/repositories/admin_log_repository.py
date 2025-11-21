"""AdminLogRepository"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from admin_web.models.admin_log import AdminLog


class AdminLogRepository:
    """
    관리자 로그 데이터 접근을 위한 Repository

    admin_logs 테이블에 대한 모든 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        AdminLogRepository를 초기화합니다.

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """
        데이터베이스 연결을 생성합니다.

        Returns:
            SQLite 데이터베이스 연결 객체
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_log(self, admin_name: str, action_type: str, target_user: Optional[str] = None, details: Optional[str] = None):
        """
        관리자 활동 로그를 생성합니다.

        Args:
            admin_name: 활동을 수행한 관리자명
            action_type: 활동 유형 (adjust_balance, role_change, warning_add 등)
            target_user: 대상 유저 ID (선택사항)
            details: 활동 상세 설명 (선택사항)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO admin_logs (admin_name, action_type, target_user, details)
            VALUES (?, ?, ?, ?)
        """, (admin_name, action_type, target_user, details))
        conn.commit()
        conn.close()

    def find_all(self, limit: int = 100) -> List[AdminLog]:
        """
        최근 관리자 로그 목록을 조회합니다.

        Args:
            limit: 조회할 최대 로그 수 (기본값: 100)

        Returns:
            최근 AdminLog 목록 (시간 역순)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [AdminLog(
            id=row['id'],
            admin_name=row['admin_name'],
            action_type=row['action_type'],
            target_user=row['target_user'],
            details=row['details'],
            timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None
        ) for row in rows]
