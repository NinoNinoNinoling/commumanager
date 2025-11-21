"""
ItemRepository

items 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.item import Item


class ItemRepository:
    """
    Item 데이터 접근을 위한 Repository
    """

    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_item(self, row: sqlite3.Row) -> Item:
        return Item(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            price=row['price'],
            category=row['category'],
            image_url=row['image_url'],
            is_active=bool(row['is_active']),
            initial_stock=row['initial_stock'],
            current_stock=row['current_stock'],
            sold_count=row['sold_count'],
            is_unlimited_stock=bool(row['is_unlimited_stock']),
            max_purchase_per_user=row['max_purchase_per_user'],
            total_sales=row['total_sales'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def create(self, item: Item) -> Item:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO items (
                name, description, price, category, image_url, is_active,
                initial_stock, current_stock, sold_count, is_unlimited_stock,
                max_purchase_per_user, total_sales
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.name, item.description, item.price, item.category, item.image_url, 1 if item.is_active else 0,
            item.initial_stock, item.current_stock, item.sold_count, 1 if item.is_unlimited_stock else 0,
            item.max_purchase_per_user, item.total_sales
        ))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.find_by_id(item_id)

    def find_by_id(self, item_id: int) -> Optional[Item]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_item(row) if row else None

    def find_all(self) -> List[Item]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows]

    def find_by_category(self, category: str) -> List[Item]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE category = ? ORDER BY created_at DESC", (category,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows]

    def find_by_active(self, is_active: bool) -> List[Item]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE is_active = ? ORDER BY created_at DESC", (1 if is_active else 0,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows]

    def update(self, item: Item) -> Item:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE items SET
                name = ?, description = ?, price = ?, category = ?, image_url = ?,
                is_active = ?, current_stock = ?, max_purchase_per_user = ?
            WHERE id = ?
        """, (
            item.name, item.description, item.price, item.category, item.image_url,
            1 if item.is_active else 0, item.current_stock, item.max_purchase_per_user,
            item.id
        ))
        conn.commit()
        conn.close()
        return self.find_by_id(item.id)

    def deactivate(self, item_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET is_active = 0 WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    def count(self) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM items")
        row = cursor.fetchone()
        conn.close()
        return row['count']

    def decrease_stock(self, item_id: int, quantity: int) -> None:
        """
        아이템 재고를 감소시키고 판매 수를 증가시킵니다.

        Args:
            item_id: 아이템 ID
            quantity: 감소시킬 수량
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE items
            SET current_stock = current_stock - ?,
                sold_count = sold_count + ?,
                total_sales = total_sales + (price * ?)
            WHERE id = ?
        """, (quantity, quantity, quantity, item_id))

        conn.commit()
        conn.close()
