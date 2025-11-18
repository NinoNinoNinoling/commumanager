"""Setting repository"""
from typing import List, Optional
from admin_web.models.setting import Setting
from admin_web.repositories.database import get_economy_db


class SettingRepository:
    """설정 데이터 저장소"""

    @staticmethod
    def find_all() -> List[Setting]:
        """전체 설정 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings ORDER BY key")
            return [Setting(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def find_by_key(key: str) -> Optional[Setting]:
        """키로 설정 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return Setting(**dict(row))
            return None

    @staticmethod
    def update(key: str, value: str) -> bool:
        """설정 업데이트"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE settings
                SET value = ?
                WHERE key = ?
            """, (value, key))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def get_value(key: str, default: str = None) -> Optional[str]:
        """설정 값 조회"""
        setting = SettingRepository.find_by_key(key)
        return setting.value if setting else default
