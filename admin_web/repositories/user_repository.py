"""User repository"""
from typing import List, Optional
from admin_web.models.user import User
from admin_web.repositories.database import get_economy_db, get_mastodon_db


class UserRepository:
    """유저 데이터 저장소"""

    @staticmethod
    def find_by_id(mastodon_id: str) -> Optional[User]:
        """ID로 유저 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE mastodon_id = ?
            """, (mastodon_id,))
            row = cursor.fetchone()
            if row:
                return User(**dict(row))
            return None

    @staticmethod
    def find_all(page: int = 1, limit: int = 50, search: str = None,
                 role: str = None, sort: str = 'created_desc') -> tuple[List[User], int]:
        """유저 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # WHERE 조건
            conditions = []
            params = []

            if search:
                conditions.append("(username LIKE ? OR display_name LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])

            if role:
                conditions.append("role = ?")
                params.append(role)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # 정렬
            sort_map = {
                'balance_desc': 'balance DESC',
                'balance_asc': 'balance ASC',
                'created_desc': 'created_at DESC',
                'created_asc': 'created_at ASC',
            }
            order_by = sort_map.get(sort, 'created_at DESC')

            # 전체 개수
            cursor.execute(f"SELECT COUNT(*) FROM users WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT * FROM users
                WHERE {where_clause}
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
            """, params + [limit, offset])

            users = [User(**dict(row)) for row in cursor.fetchall()]
            return users, total

    @staticmethod
    def create(user: User) -> User:
        """유저 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (mastodon_id, username, display_name, role, dormitory)
                VALUES (?, ?, ?, ?, ?)
            """, (user.mastodon_id, user.username, user.display_name, user.role, user.dormitory))
            conn.commit()
            return UserRepository.find_by_id(user.mastodon_id)

    @staticmethod
    def update_role(mastodon_id: str, role: str) -> bool:
        """역할 변경"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET role = ? WHERE mastodon_id = ?
            """, (role, mastodon_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def update_balance(mastodon_id: str, amount: int) -> bool:
        """재화 조정"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            if amount > 0:
                cursor.execute("""
                    UPDATE users
                    SET balance = balance + ?, total_earned = total_earned + ?
                    WHERE mastodon_id = ?
                """, (amount, amount, mastodon_id))
            else:
                cursor.execute("""
                    UPDATE users
                    SET balance = balance + ?, total_spent = total_spent + ?
                    WHERE mastodon_id = ?
                """, (amount, abs(amount), mastodon_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def get_activity_48h(mastodon_id: str) -> int:
        """48시간 답글 수 조회 (PostgreSQL)"""
        try:
            with get_mastodon_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM statuses
                    WHERE account_id = %s
                    AND in_reply_to_id IS NOT NULL
                    AND created_at > NOW() - INTERVAL '48 hours'
                """, (mastodon_id,))
                return cursor.fetchone()[0]
        except Exception:
            return 0

    @staticmethod
    def count_all() -> int:
        """전체 사용자 수 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

    @staticmethod
    def count_active_since(since_datetime) -> int:
        """특정 시간 이후 활동한 사용자 수 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM users
                WHERE last_active > ?
            """, (since_datetime.isoformat(),))
            return cursor.fetchone()[0]
