"""
UserStatsRepository

user_stats 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Dict, Any

class UserStatsRepository:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def find_risk_users(self, system_roles: List[str]) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(system_roles))
        query = f"""
            SELECT
                u.username,
                u.display_name,
                u.role_name,
                s.*
            FROM user_stats s
            JOIN users u ON s.user_id = u.mastodon_id
            WHERE (s.is_isolated = 1 OR s.is_biased = 1 OR s.is_avoiding = 1 OR s.is_inactive = 1)
              AND (u.role_name IS NULL OR u.role_name = ''
                   OR u.role_name NOT IN ({placeholders}))
            ORDER BY s.analyzed_at DESC
        """
        cursor.execute(query, system_roles)
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            risk_types = []
            if row['is_isolated']: risk_types.append({'type': '고립 위험', 'class': 'bg-primary'})
            if row['is_biased']: risk_types.append({'type': '편향 위험', 'class': 'bg-warning text-dark'})
            if row['is_avoiding']: risk_types.append({'type': '회피 패턴', 'class': 'bg-danger'})
            if row['is_inactive']: risk_types.append({'type': '답글 미달', 'class': 'bg-info text-dark'})

            result.append({
                'username': row['username'],
                'display_name': row['display_name'],
                'risk_types': risk_types,
                'detail': '소수 인원과만 대화' if row['is_isolated'] else '특정인 편향'
            })
        return result
