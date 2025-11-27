"""
ItemRepository

items 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from admin_web.models.item import Item
from admin_web.utils.datetime_utils import parse_datetime


class ItemRepository:
    """
    Item 데이터 접근을 위한 Repository

    items 테이블에 대한 모든 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        ItemRepository를 초기화합니다.

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

    def _row_to_item(self, row: sqlite3.Row) -> Item:
        """
        데이터베이스 Row를 Item 모델로 변환합니다.

        Args:
            row: 데이터베이스 조회 결과 Row

        Returns:
            변환된 Item 객체
        """
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
            created_at=parse_datetime(row['created_at'])
        )

    def create(self, item: Item) -> Item:
        """
        새 아이템을 생성합니다.

        Args:
            item: 생성할 Item 객체

        Returns:
            생성된 Item 객체
        """
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
        """
        ID로 아이템을 조회합니다.

        Args:
            item_id: 아이템 ID

        Returns:
            조회된 Item 객체, 없으면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_item(row) if row else None

    def find_all(self) -> List[Item]:
        """
        모든 아이템을 조회합니다.

        Returns:
            모든 Item 목록 (생성일시 역순)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows]

    def find_by_category(self, category: str) -> List[Item]:
        """
        특정 카테고리의 아이템 목록을 조회합니다.

        Args:
            category: 카테고리명

        Returns:
            해당 카테고리의 Item 목록
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE category = ? ORDER BY created_at DESC", (category,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows]

    def find_by_active(self, is_active: bool) -> List[Item]:
        """
        활성 상태별 아이템 목록을 조회합니다.

        Args:
            is_active: 활성화 여부

        Returns:
            해당 활성 상태의 Item 목록
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE is_active = ? ORDER BY created_at DESC", (1 if is_active else 0,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows]

    def update(self, item: Item) -> Item:
        """
        아이템 정보를 업데이트합니다.

        Args:
            item: 업데이트할 Item 객체

        Returns:
            업데이트된 Item 객체
        """
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
        """
        아이템을 비활성화합니다.

        Args:
            item_id: 비활성화할 아이템 ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET is_active = 0 WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    def count(self) -> int:
        """
        전체 아이템 개수를 조회합니다.

        Returns:
            아이템 총 개수
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM items")
        row = cursor.fetchone()
        conn.close()
        return row['count']

    def decrease_stock(self, item_id: int, quantity: int, connection=None) -> None:
        """
        아이템 재고를 감소시키고 판매 수를 증가시킵니다.

        Args:
            item_id: 아이템 ID
            quantity: 감소시킬 수량
            connection: 트랜잭션용 연결 (선택사항)
        """
        conn = connection or self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE items
            SET current_stock = current_stock - ?,
                sold_count = sold_count + ?,
                total_sales = total_sales + (price * ?)
            WHERE id = ?
        """, (quantity, quantity, quantity, item_id))

        if connection is None:  # 독립 호출이면 자동 커밋
            conn.commit()
            conn.close()
