"""Item service"""
from typing import List, Optional
from admin_web.models.item import Item
from admin_web.repositories.item_repository import ItemRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository
from admin_web.models.admin_log import AdminLog


class ItemService:
    """아이템 비즈니스 로직"""

    def __init__(self):
        self.item_repo = ItemRepository()
        self.admin_log_repo = AdminLogRepository()

    def get_items(self, page: int = 1, limit: int = 50, is_active: bool = None) -> dict:
        """아이템 목록 조회"""
        items, total = self.item_repo.find_all(page, limit, is_active)
        total_pages = (total + limit - 1) // limit

        return {
            'items': [i.to_dict() for i in items],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }

    def get_item(self, item_id: int) -> Optional[Item]:
        """아이템 조회"""
        return self.item_repo.find_by_id(item_id)

    def create_item(self, item_data: dict) -> Item:
        """아이템 생성"""
        # 1. 아이템 생성
        item = Item(
            id=None,
            name=item_data['name'],
            description=item_data.get('description'),
            price=item_data.get('price', 0),
            category=item_data.get('category'),
            image_url=item_data.get('image_url'),
            is_active=item_data.get('is_active', True),
        )
        created_item = self.item_repo.create(item)

        # 2. 관리자 로그 생성
        admin_name = item_data.get('admin_name')
        if admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='create_item',
                details=f"{item_data['name']} (가격: {item_data.get('price', 0)})",
            )
            self.admin_log_repo.create(log)

        return created_item

    def update_item(self, item_id: int, item_data: dict) -> bool:
        """아이템 수정"""
        # 기존 아이템 조회
        existing_item = self.item_repo.find_by_id(item_id)
        if not existing_item:
            return False

        # 업데이트할 아이템 생성
        item = Item(
            id=item_id,
            name=item_data.get('name', existing_item.name),
            description=item_data.get('description', existing_item.description),
            price=item_data.get('price', existing_item.price),
            category=item_data.get('category', existing_item.category),
            image_url=item_data.get('image_url', existing_item.image_url),
            is_active=item_data.get('is_active', existing_item.is_active),
        )
        success = self.item_repo.update(item)

        # 관리자 로그 생성
        admin_name = item_data.get('admin_name')
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='update_item',
                details=f"{item.name} (id: {item_id}, 가격: {item.price})",
            )
            self.admin_log_repo.create(log)

        return success

    def delete_item(self, item_id: int, admin_name: str = None) -> bool:
        """아이템 삭제"""
        success = self.item_repo.delete(item_id)

        # 관리자 로그 생성
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='delete_item',
                details=f"item_id: {item_id}",
            )
            self.admin_log_repo.create(log)

        return success
