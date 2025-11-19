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

    def create_item(self, name: str, description: str = None, price: int = 0,
                    is_active: bool = True, admin_name: str = None) -> Item:
        """아이템 생성"""
        # 1. 아이템 생성
        item = Item(
            id=None,
            name=name,
            description=description,
            price=price,
            is_active=is_active,
        )
        created_item = self.item_repo.create(item)

        # 2. 관리자 로그 생성
        if admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action='create_item',
                details=f"{name} (가격: {price})",
            )
            self.admin_log_repo.create(log)

        return created_item

    def update_item(self, item_id: int, name: str, description: str = None,
                    price: int = 0, is_active: bool = True,
                    admin_name: str = None) -> bool:
        """아이템 수정"""
        item = Item(
            id=item_id,
            name=name,
            description=description,
            price=price,
            is_active=is_active,
        )
        success = self.item_repo.update(item)

        # 관리자 로그 생성
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action='update_item',
                details=f"{name} (id: {item_id}, 가격: {price})",
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
                action='delete_item',
                details=f"item_id: {item_id}",
            )
            self.admin_log_repo.create(log)

        return success
