"""ItemService"""
from typing import List, Dict, Any

from admin_web.models.item import Item
from admin_web.repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path
        self.item_repo = ItemRepository(db_path)

    def create_item(self, item: Item) -> Dict[str, Any]:
        if item.price < 0:
            raise ValueError('Price must be positive')
        created = self.item_repo.create(item)
        return {'item': created}

    def get_active_items(self) -> List[Item]:
        return self.item_repo.find_by_active(True)

    def get_item(self, item_id: int) -> Item:
        return self.item_repo.find_by_id(item_id)
