import sqlite3
from typing import List, Dict, Any

class TransactionService:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_user_transactions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """특정 유저의 거래 내역 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                id,
                transaction_type,
                amount,
                category,
                description,
                timestamp,
                admin_name
            FROM transactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """
        
        cursor.execute(query, (user_id, limit, offset))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_transaction_stats(self, user_id: str) -> Dict[str, int]:
        """유저의 누적 획득/사용량 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                total_earned, 
                total_spent 
            FROM users 
            WHERE mastodon_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return {'total_earned': 0, 'total_spent': 0}
