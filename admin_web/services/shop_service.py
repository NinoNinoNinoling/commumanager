"""ShopService"""
from typing import Dict, Any

from admin_web.repositories.item_repository import ItemRepository
from admin_web.repositories.inventory_repository import InventoryRepository
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository
from admin_web.models.inventory import Inventory
from admin_web.models.transaction import Transaction


class ShopService:
    """
    상점 비즈니스 로직을 처리하는 Service

    아이템 구매, 재고 관리 등의 상점 관련 기능을 제공합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        ShopService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.item_repo = ItemRepository(db_path)
        self.inventory_repo = InventoryRepository(db_path)
        self.user_repo = UserRepository(db_path)
        self.transaction_repo = TransactionRepository(db_path)

    def purchase_item(self, user_id: str, item_id: int, quantity: int = 1) -> Dict[str, Any]:
        """
        아이템을 구매합니다.

        잔액 차감, 재고 감소, 인벤토리 추가, 거래 기록이 함께 처리됩니다.

        Args:
            user_id: 구매자의 Mastodon ID
            item_id: 구매할 아이템 ID
            quantity: 구매 수량

        Returns:
            구매 결과 딕셔너리:
            - success: 성공 여부
            - error: 실패 시 오류 메시지
            - item, quantity, total_price, new_balance: 성공 시 정보
        """
        try:
            # 아이템 조회 및 검증
            item = self.item_repo.find_by_id(item_id)
            if not item or not item.is_purchasable():
                return {'success': False, 'error': 'Item is not available for purchase'}

            # 유저 조회
            user = self.user_repo.find_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}

            # 총 가격 계산
            total_price = item.price * quantity

            # 잔액 확인
            if user.balance < total_price:
                return {'success': False, 'error': 'Insufficient balance'}

            # 재고 확인 (무제한이 아닌 경우)
            if not item.is_unlimited_stock and item.current_stock < quantity:
                return {'success': False, 'error': 'Insufficient stock'}

            # Repository 계층을 통해 처리
            try:
                # 1. 유저 잔액 차감 (Repository 사용)
                self.user_repo.adjust_balance(user_id, -total_price)

                # 2. 아이템 재고 감소 (Repository 사용, 무제한 재고가 아닌 경우)
                if not item.is_unlimited_stock:
                    self.item_repo.decrease_stock(item_id, quantity)

                # 3. 인벤토리에 추가 (Repository 사용)
                inventory = Inventory(user_id=user_id, item_id=item_id, quantity=quantity)
                self.inventory_repo.add_or_update(inventory)

                # 4. 거래 기록 생성 (Repository 사용)
                transaction = Transaction(
                    user_id=user_id,
                    amount=-total_price,
                    transaction_type='purchase',
                    description=f'구매: {item.name} x{quantity}',
                    category='shop'
                )
                self.transaction_repo.create(transaction)

                # 5. 업데이트된 유저 조회
                updated_user = self.user_repo.find_by_id(user_id)

                return {
                    'success': True,
                    'item': item,
                    'quantity': quantity,
                    'total_price': total_price,
                    'new_balance': updated_user.balance
                }

            except ValueError as e:
                # Repository에서 발생한 검증 오류 (예: 잔액 부족)
                return {'success': False, 'error': str(e)}
            except Exception as e:
                # 기타 오류
                return {'success': False, 'error': f'Purchase failed: {str(e)}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}
