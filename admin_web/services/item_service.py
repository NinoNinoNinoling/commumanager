"""ItemService"""
from typing import List, Dict, Any, Optional

from admin_web.models.item import Item
from admin_web.repositories.item_repository import ItemRepository


class ItemService:
    """
    아이템 관리 비즈니스 로직을 위한 Service

    상점 아이템의 생성, 조회, 활성화 관리를 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path
        self.item_repo = ItemRepository(db_path)

    def create_item(self, item: Item) -> Dict[str, Any]:
        """아이템을 생성합니다."""
        if item.price < 0:
            raise ValueError('Price must be positive')
        created = self.item_repo.create(item)
        return {'item': created}

    def get_active_items(self) -> List[Item]:
        """활성 상태인 아이템 목록을 조회합니다."""
        return self.item_repo.find_by_active(True)

    def get_item(self, item_id: int) -> Optional[Item]:
        """ID로 아이템을 조회합니다."""
        return self.item_repo.find_by_id(item_id)
