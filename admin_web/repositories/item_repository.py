"""Item repository"""
from typing import List, Optional
from admin_web.models.item import Item
from admin_web.repositories.database import get_economy_db


class ItemRepository:
    """아이템 데이터 저장소"""

    @staticmethod
    def find_all(page: int = 1, limit: int = 50, is_active: bool = None) -> tuple[List[Item], int]:
        """아이템 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # WHERE 조건
            where_clause = "is_active = ?" if is_active is not None else "1=1"
            params = [1 if is_active else 0] if is_active is not None else []

            # 전체 개수
            cursor.execute(f"SELECT COUNT(*) FROM items WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT * FROM items
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])

            items = [Item(**dict(row)) for row in cursor.fetchall()]
            return items, total

    @staticmethod
    def find_by_id(item_id: int) -> Optional[Item]:
        """ID로 아이템 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if row:
                return Item(**dict(row))
            return None

    @staticmethod
    def create(item: Item) -> Item:
        """아이템 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO items (name, description, price, is_active)
                VALUES (?, ?, ?, ?)
            """, (item.name, item.description, item.price, 1 if item.is_active else 0))
            conn.commit()

            # 생성된 ID로 조회
            item_id = cursor.lastrowid
            return ItemRepository.find_by_id(item_id)

    @staticmethod
    def update(item: Item) -> bool:
        """아이템 수정"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE items
                SET name = ?, description = ?, price = ?, is_active = ?
                WHERE id = ?
            """, (item.name, item.description, item.price, 1 if item.is_active else 0, item.id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(item_id: int) -> bool:
        """아이템 삭제"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0
