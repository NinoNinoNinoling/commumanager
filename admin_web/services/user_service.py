import sqlite3
from typing import List, Dict, Any, Optional
from admin_web.models.user import User
from admin_web.models.transaction import Transaction
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository
from admin_web.constants import SYSTEM_ROLES
from datetime import datetime
from flask import current_app # Import current_app


class UserService:
    """
    유저 관리 비즈니스 로직을 위한 Service

    유저 조회, 잔액 조정, 위험 감지 유저 조회 등의 기능을 제공합니다.
    UserRepository와 TransactionRepository를 사용하여 DB에 접근합니다.
    """

    def __init__(self, db_path: str = None):
        """
        UserService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로 (제공되지 않으면 앱 컨텍스트에서 가져옴)
        """
        if db_path is None:
            self.db_path = current_app.config.get('DATABASE_PATH', 'economy.db')
        else:
            self.db_path = db_path
        self.user_repo = UserRepository(self.db_path)
        self.transaction_repo = TransactionRepository(self.db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """
        데이터베이스 연결을 가져옵니다.

        복잡한 조인 쿼리(get_risk_users, get_all_users 등)를 위해 필요합니다.
        단순 CRUD는 Repository를 사용하세요.

        Returns:
            SQLite 연결 객체
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Mastodon ID를 사용하여 유저 상세 정보를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            찾은 경우 User 객체, 아니면 None
        """
        return self.user_repo.find_by_id(user_id)

    def get_all_users(self) -> List[User]: # Changed return type to List[User]
        """
        전체 유저를 조회합니다 (시스템 계정 제외).

        시스템 계정(Owner, Admin, Moderator, 봇 등)은 필터링됩니다.

        Returns:
            시스템 계정을 제외한 모든 유저 리스트 (생성일시 역순)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        placeholders = ','.join(['?'] * len(SYSTEM_ROLES))
        query = f"""
            SELECT * FROM users
            WHERE role_name IS NULL
               OR role_name NOT IN ({placeholders})
            ORDER BY created_at DESC
        """

        cursor.execute(query, list(SYSTEM_ROLES))
        rows = cursor.fetchall()
        conn.close()
        return [User(**dict(row)) for row in rows] # Return User objects


    def update_user_role(self, user_id: str, new_role: str) -> User:
        """
        유저의 역할을 업데이트합니다.

        Args:
            user_id: 유저의 Mastodon ID
            new_role: 변경할 새로운 역할 (user, admin, moderator)

        Returns:
            업데이트된 User 객체

        Raises:
            ValueError: 유저를 찾을 수 없거나 역할이 유효하지 않을 경우
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("유저를 찾을 수 없습니다.")

        # 역할 유효성 검사 (필요에 따라 더 상세한 검증 추가)
        allowed_roles = ['user', 'admin', 'moderator']
        if new_role not in allowed_roles:
            raise ValueError(f"유효하지 않은 역할입니다: {new_role}. 허용된 역할: {', '.join(allowed_roles)}")
        
        self.user_repo.update_role(user_id, new_role)
        return self.user_repo.find_by_id(user_id) # 업데이트된 유저 정보 반환
        
    def get_risk_users(self) -> List[Dict]:
        """
        위험 감지 유저를 조회합니다 (시스템 계정 제외).

        user_stats 테이블과 조인하여 고립/편향/회피/비활성 위험이 있는 유저를 조회합니다.
        시스템 계정은 필터링됩니다.

        Returns:
            위험 유저 정보 리스트 (각 항목은 username, display_name, risk_types, detail 포함)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        placeholders = ','.join(['?'] * len(SYSTEM_ROLES))

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

        cursor.execute(query, list(SYSTEM_ROLES))
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
        유저 잔액을 조정하고 거래 내역을 기록합니다.

        잔액 업데이트와 거래 기록 생성은 단일 DB 트랜잭션으로 원자적으로 처리됩니다.
        음수 잔액은 허용되지 않습니다.

        Args:
            user_id: 유저의 Mastodon ID
            amount: 조정할 금액 (양수: 입금, 음수: 출금)
            transaction_type: 거래 유형 (adjustment, reward 등)
            description: 거래 설명
            admin_name: 조정을 수행한 관리자명 (선택)

        Returns:
            조정 결과 딕셔너리 (status, user_id, new_balance, transaction_id)

        Raises:
            ValueError: 금액이 0이거나, 유저가 없거나, 잔액이 음수가 되는 경우

        Note:
            이 메서드는 트랜잭션 원자성 보장을 위해 직접 DB 접근을 수행합니다.
        """
        if not isinstance(amount, int) or amount == 0:
            raise ValueError("유효한 금액(정수)을 입력해야 합니다.")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT balance, total_earned, total_spent FROM users WHERE mastodon_id = ?", (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                raise ValueError("유저를 찾을 수 없습니다.")

            current_balance = user_data['balance']
            new_balance = current_balance + amount

            if new_balance < 0:
                raise ValueError("잔액이 0 미만이 될 수 없습니다.")

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

            transaction_query = """
                INSERT INTO transactions (user_id, transaction_type, amount, category, description, admin_name, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            category = "관리자 조정"
            timestamp = datetime.now().isoformat()

            cursor.execute(transaction_query,
                           (user_id, transaction_type, amount, category, description, admin_name, timestamp))

            transaction_id = cursor.lastrowid
            conn.commit()

            return {
                'status': 'success',
                'user_id': user_id,
                'new_balance': new_balance,
                'transaction_id': transaction_id
            }

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            conn.close()
