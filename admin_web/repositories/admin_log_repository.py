"""Admin Log repository"""
from typing import List, Optional
from admin_web.models.admin_log import AdminLog
from admin_web.repositories.database import get_economy_db


class AdminLogRepository:
    """관리자 로그 데이터 저장소"""

    @staticmethod
    def find_all(page: int = 1, limit: int = 50, admin_name: str = None,
                 action_type: str = None) -> tuple[List[AdminLog], int]:
        """로그 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # WHERE 조건
            conditions = []
            params = []

            if admin_name:
                conditions.append("admin_name = ?")
                params.append(admin_name)

            if action_type:
                conditions.append("action_type = ?")
                params.append(action_type)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # 전체 개수
            cursor.execute(f"SELECT COUNT(*) FROM admin_logs WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT * FROM admin_logs
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])

            logs = [AdminLog(**dict(row)) for row in cursor.fetchall()]
            return logs, total

    @staticmethod
    def create(log: AdminLog) -> AdminLog:
        """로그 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO admin_logs (admin_name, action_type, target_user, details)
                VALUES (?, ?, ?, ?)
            """, (log.admin_name, log.action_type, log.target_user, log.details))
            conn.commit()

            # 생성된 ID로 조회
            log_id = cursor.lastrowid
            cursor.execute("SELECT * FROM admin_logs WHERE id = ?", (log_id,))
            row = cursor.fetchone()
            return AdminLog(**dict(row))
