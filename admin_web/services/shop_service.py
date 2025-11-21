"""ShopService"""
import sqlite3
from typing import Dict, Any

from admin_web.repositories.item_repository import ItemRepository
from admin_web.repositories.inventory_repository import InventoryRepository
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository
from admin_web.models.inventory import Inventory
from admin_web.models.transaction import Transaction


class ShopService:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path
        self.item_repo = ItemRepository(db_path)
        self.inventory_repo = InventoryRepository(db_path)
        self.user_repo = UserRepository(db_path)
        self.transaction_repo = TransactionRepository(db_path)

    def purchase_item(self, user_id: str, item_id: int, quantity: int = 1) -> Dict[str, Any]:
        try:
            # Get item
            item = self.item_repo.find_by_id(item_id)
            if not item or not item.is_purchasable():
                return {'success': False, 'error': 'Item is not available for purchase'}

            # Get user
            user = self.user_repo.find_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}

            # Calculate total price
            total_price = item.price * quantity

            # Check balance
            if user.balance < total_price:
                return {'success': False, 'error': 'Insufficient balance'}

            # Perform purchase (트랜잭션)
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Update user balance
                cursor.execute("UPDATE users SET balance = balance - ? WHERE mastodon_id = ?", 
                             (total_price, user_id))
                
                # Update item stock if not unlimited
                if not item.is_unlimited_stock:
                    cursor.execute("UPDATE items SET current_stock = current_stock - ?, sold_count = sold_count + ? WHERE id = ?",
                                 (quantity, quantity, item_id))
                
                # Add to inventory
                inventory = Inventory(user_id=user_id, item_id=item_id, quantity=quantity)
                cursor.execute("SELECT * FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?",
                                 (quantity, user_id, item_id))
                else:
                    cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)",
                                 (user_id, item_id, quantity))
                
                # Create transaction record
                cursor.execute("""
                    INSERT INTO transactions (user_id, amount, transaction_type, description)
                    VALUES (?, ?, ?, ?)
                """, (user_id, -total_price, 'purchase', f'구매: {item.name} x{quantity}'))
                
                conn.commit()
                
                # Get new balance
                cursor.execute("SELECT balance FROM users WHERE mastodon_id = ?", (user_id,))
                new_balance = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'item': item,
                    'quantity': quantity,
                    'total_price': total_price,
                    'new_balance': new_balance
                }
            except Exception as e:
                conn.rollback()
                return {'success': False, 'error': str(e)}
            finally:
                conn.close()
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
