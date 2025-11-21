"""InventoryRepository"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.inventory import Inventory


class InventoryRepository:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_inventory(self, row: sqlite3.Row) -> Inventory:
        return Inventory(
            id=row['id'],
            user_id=row['user_id'],
            item_id=row['item_id'],
            quantity=row['quantity'],
            acquired_at=datetime.fromisoformat(row['acquired_at']) if row['acquired_at'] else None
        )

    def add_or_update(self, inventory: Inventory) -> Inventory:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("SELECT * FROM inventory WHERE user_id = ? AND item_id = ?", (inventory.user_id, inventory.item_id))
        existing = cursor.fetchone()
        
        if existing:
            new_quantity = existing['quantity'] + inventory.quantity
            cursor.execute("UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?",
                         (new_quantity, inventory.user_id, inventory.item_id))
            result_id = existing['id']
        else:
            cursor.execute("""
                INSERT INTO inventory (user_id, item_id, quantity)
                VALUES (?, ?, ?)
            """, (inventory.user_id, inventory.item_id, inventory.quantity))
            result_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE id = ?", (result_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_inventory(row)

    def find_by_user(self, user_id: str) -> List[Inventory]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE user_id = ? ORDER BY acquired_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_inventory(row) for row in rows]

    def user_owns_item(self, user_id: str, item_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
        row = cursor.fetchone()
        conn.close()
        return row['count'] > 0
