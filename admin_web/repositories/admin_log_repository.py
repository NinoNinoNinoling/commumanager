import sqlite3
from admin_web.models.admin_log import AdminLog
from datetime import datetime

class AdminLogRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_log(self, admin_id: str, action: str, target_type: str, target_id: str, details: str, ip: str = None):
        """로그 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action_type, target_type, target_id, details, ip_address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (admin_id, action, target_type, target_id, details, ip))
        conn.commit()
        conn.close()
