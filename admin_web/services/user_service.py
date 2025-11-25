import sqlite3
from typing import List, Dict, Optional
from admin_web.models.user import User

class UserService:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path
        # 필터링할 시스템 역할 목록
        self.SYSTEM_ROLES = {'Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트'}

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_users(self) -> List[User]:
        """전체 유저 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [User(**dict(row)) for row in rows]

    def get_risk_users(self) -> List[Dict]:
        """
        위험 감지 유저 조회 (시스템 계정 제외)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 시스템 역할을 제외하는 조건 추가
        placeholders = ','.join(['?'] * len(self.SYSTEM_ROLES))
        
        query = f"""
            SELECT 
                u.username, 
                u.display_name,
                u.role_name,
                s.*
            FROM user_stats s
            JOIN users u ON s.user_id = u.mastodon_id
            WHERE (s.is_isolated = 1 OR s.is_biased = 1 OR s.is_avoiding = 1 OR s.is_inactive = 1)
              AND (u.role_name IS NULL OR u.role_name NOT IN ({placeholders}))
            ORDER BY s.analyzed_at DESC
        """
        
        cursor.execute(query, list(self.SYSTEM_ROLES))
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            # 위험 유형 판별
            risk_types = []
            if row['is_isolated']: risk_types.append({'type': '고립 위험', 'class': 'bg-primary'})
            if row['is_biased']: risk_types.append({'type': '편향 위험', 'class': 'bg-warning text-dark'})
            if row['is_avoiding']: risk_types.append({'type': '회피 패턴', 'class': 'bg-danger'})
            if row['is_inactive']: risk_types.append({'type': '답글 미달', 'class': 'bg-info text-dark'})

            result.append({
                'username': row['username'],
                'display_name': row['display_name'],
                'risk_types': risk_types,
                # 상세 지표 (예시 로직)
                'detail': '소수 인원과만 대화' if row['is_isolated'] else '특정인 편향'
            })
            
        return result
