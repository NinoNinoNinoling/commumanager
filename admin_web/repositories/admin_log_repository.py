import sqlite3
from admin_web.models.admin_log import AdminLog
from datetime import datetime

class AdminLogRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_log(self, admin_name: str, action_type: str, target_user: str = None, details: str = None):
        """로그 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO admin_logs (admin_name, action_type, target_user, details)
            VALUES (?, ?, ?, ?)
        """, (admin_name, action_type, target_user, details))
        conn.commit()
        conn.close()
