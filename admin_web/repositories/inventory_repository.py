"""InventoryRepository"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.inventory import Inventory
from admin_web.utils.datetime_utils import parse_datetime


class InventoryRepository:
    """
    인벤토리 데이터 접근을 위한 Repository

    inventory 테이블에 대한 모든 CRUD 작업을 처리합니다.
    유저의 아이템 보유 정보를 관리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        InventoryRepository를 초기화합니다.

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """
        데이터베이스 연결을 생성합니다.

        Returns:
            SQLite 데이터베이스 연결 객체
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_inventory(self, row: sqlite3.Row) -> Inventory:
        """
        데이터베이스 Row를 Inventory 모델로 변환합니다.

        Args:
            row: 데이터베이스 조회 결과 Row

        Returns:
            변환된 Inventory 객체
        """
        return Inventory(
            id=row['id'],
            user_id=row['user_id'],
            item_id=row['item_id'],
            quantity=row['quantity'],
            acquired_at=parse_datetime(row['acquired_at'])
        )

    def add_or_update(self, inventory: Inventory, connection=None) -> Inventory:
        """
        인벤토리에 아이템을 추가하거나 수량을 업데이트합니다.

        이미 보유한 아이템이면 수량을 증가시키고, 없으면 새로 추가합니다.

        Args:
            inventory: 추가/업데이트할 Inventory 객체
            connection: 트랜잭션용 연결 (선택사항)

        Returns:
            추가/업데이트된 Inventory 객체
        """
        conn = connection or self._get_connection()
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

        if connection is None:  # 독립 호출이면 자동 커밋
            conn.commit()

        # Fetch the updated/created record
        cursor.execute("SELECT * FROM inventory WHERE id = ?", (result_id,))
        row = cursor.fetchone()

        if connection is None:
            conn.close()

        return self._row_to_inventory(row)

    def find_by_user(self, user_id: str) -> List[Inventory]:
        """
        특정 유저의 인벤토리 목록을 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저가 보유한 Inventory 목록 (획득일시 역순)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE user_id = ? ORDER BY acquired_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_inventory(row) for row in rows]

    def user_owns_item(self, user_id: str, item_id: int) -> bool:
        """
        유저가 특정 아이템을 보유하고 있는지 확인합니다.

        Args:
            user_id: 유저의 Mastodon ID
            item_id: 아이템 ID

        Returns:
            보유 중이면 True, 아니면 False
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
        row = cursor.fetchone()
        conn.close()
        return row['count'] > 0
