"""
SettingsRepository
"""
import sqlite3
from typing import List, Optional
from admin_web.models.setting import Setting

class SettingsRepository:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_setting(self, row: sqlite3.Row) -> Setting:
        return Setting.from_dict(dict(row))

    def find_all(self) -> List[Setting]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings ORDER BY key")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_setting(row) for row in rows]

    def find_by_key(self, key: str) -> Optional[Setting]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_setting(row) if row else None

    def update(self, key: str, value: str, admin_name: str) -> Optional[Setting]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE settings SET value = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
            (value, admin_name, key)
        )
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return self.find_by_key(key) if rows_affected > 0 else None
