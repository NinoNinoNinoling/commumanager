import sqlite3
from typing import List, Dict, Any, Optional
from admin_web.models.user import User
from datetime import datetime

class UserService:
    
    SYSTEM_ROLES = {'Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트'}

    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        # WAL(Write-Ahead Logging) 모드를 사용하여 동시성 확보
        conn.execute("PRAGMA journal_mode = WAL") 
        conn.row_factory = sqlite3.Row
        return conn

    def get_user(self, user_id: str) -> Optional[User]:
        """Mastodon ID를 사용하여 유저 상세 정보를 조회합니다."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM users WHERE mastodon_id = ?"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(**dict(row))
        return None

    def get_all_users(self) -> List[User]:
        """전체 유저 조회 (시스템 계정 제외)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join(['?'] * len(self.SYSTEM_ROLES))
        query = f"""
            SELECT * FROM users
            WHERE role_name IS NULL 
               OR role_name NOT IN ({placeholders})
            ORDER BY created_at DESC
        """
        
        cursor.execute(query, list(self.SYSTEM_ROLES))
        rows = cursor.fetchall()
        conn.close()
        return [User(**dict(row)) for row in rows]

    def get_risk_users(self) -> List[Dict]:
        """위험 감지 유저 조회 (시스템 계정 제외)"""
        conn = self._get_connection()
        cursor = conn.cursor()

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
        
    def adjust_balance(self, user_id: str, amount: int, transaction_type: str, description: str, admin_name: Optional[str] = None) -> Dict[str, Any]:
        """
        [핵심 로직] 잔액을 조정하고 거래 내역을 기록합니다.
        
        잔액 업데이트와 내역 기록은 단일 DB 트랜잭션으로 처리됩니다.
        """
        if not isinstance(amount, int) or amount == 0:
            raise ValueError("유효한 금액(정수)을 입력해야 합니다.")
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. 유저의 현재 잔액과 누적 통계를 조회
            cursor.execute("SELECT balance, total_earned, total_spent FROM users WHERE mastodon_id = ?", (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                raise ValueError("유저를 찾을 수 없습니다.")
                
            current_balance = user_data['balance']
            
            # 2. 잔액 변경 유효성 검사 (음수 잔액 방지)
            new_balance = current_balance + amount
            if new_balance < 0:
                raise ValueError("잔액이 0 미만이 될 수 없습니다.")
            
            # 3. users 테이블 업데이트 (balance, total_earned, total_spent)
            update_fields = ['balance = ?']
            update_values = [new_balance]
            
            if amount > 0:
                update_fields.append('total_earned = total_earned + ?')
                update_values.append(amount)
            else:
                update_fields.append('total_spent = total_spent + ?')
                update_values.append(abs(amount))
                
            update_values.append(user_id)
            
            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE mastodon_id = ?"
            cursor.execute(update_query, update_values)
            
            # 4. transactions 테이블에 새 내역 기록
            transaction_query = """
                INSERT INTO transactions (user_id, transaction_type, amount, category, description, admin_name, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            category = "관리자 조정"
            timestamp = datetime.now().isoformat()
            
            cursor.execute(transaction_query, 
                           (user_id, transaction_type, amount, category, description, admin_name, timestamp))
                           
            transaction_id = cursor.lastrowid
            
            # 5. 트랜잭션 커밋
            conn.commit()
            
            return {
                'status': 'success', 
                'user_id': user_id, 
                'new_balance': new_balance, 
                'transaction_id': transaction_id
            }
            
        except Exception as e:
            conn.rollback() # 오류 발생 시 롤백
            raise e
            
        finally:
            conn.close()
