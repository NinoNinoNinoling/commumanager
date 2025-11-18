"""Warning repository"""
from typing import List, Optional
from admin_web.models.warning import Warning
from admin_web.repositories.database import get_economy_db


class WarningRepository:
    """경고 데이터 저장소"""

    @staticmethod
    def find_all(page: int = 1, limit: int = 50) -> tuple[List[Warning], int]:
        """경고 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 전체 개수
            cursor.execute("SELECT COUNT(*) FROM warnings")
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute("""
                SELECT * FROM warnings
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            warnings = [Warning(**dict(row)) for row in cursor.fetchall()]
            return warnings, total

    @staticmethod
    def find_by_user(user_id: str, page: int = 1, limit: int = 50) -> tuple[List[Warning], int]:
        """유저별 경고 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 전체 개수
            cursor.execute("SELECT COUNT(*) FROM warnings WHERE user_id = ?", (user_id,))
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute("""
                SELECT * FROM warnings
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))

            warnings = [Warning(**dict(row)) for row in cursor.fetchall()]
            return warnings, total

    @staticmethod
    def create(warning: Warning) -> Warning:
        """경고 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO warnings (user_id, reason, count, admin_name)
                VALUES (?, ?, ?, ?)
            """, (warning.user_id, warning.reason, warning.count, warning.admin_name))
            conn.commit()

            # 생성된 ID로 조회
            warning_id = cursor.lastrowid
            cursor.execute("SELECT * FROM warnings WHERE id = ?", (warning_id,))
            row = cursor.fetchone()
            return Warning(**dict(row))

    @staticmethod
    def count_by_user(user_id: str) -> int:
        """유저별 경고 수"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM warnings WHERE user_id = ?", (user_id,))
            return cursor.fetchone()[0]

    @staticmethod
    def count_this_week() -> int:
        """이번 주 경고 수"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM warnings
                WHERE timestamp > datetime('now', '-7 days')
            """)
            return cursor.fetchone()[0]
