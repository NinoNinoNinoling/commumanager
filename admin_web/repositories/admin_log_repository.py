"""AdminLogRepository"""
import sqlite3
from typing import List
from datetime import datetime
from admin_web.models.admin_log import AdminLog


class AdminLogRepository:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_log(self, admin_name: str, action_type: str, target_user: str = None, details: str = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO admin_logs (admin_name, action_type, target_user, details)
            VALUES (?, ?, ?, ?)
        """, (admin_name, action_type, target_user, details))
        conn.commit()
        conn.close()

    def find_all(self, limit: int = 100) -> List[AdminLog]:
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
