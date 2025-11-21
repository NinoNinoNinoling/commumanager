"""ItemController"""
from flask import request, jsonify
from admin_web.services.item_service import ItemService
from admin_web.services.shop_service import ShopService
from admin_web.models.item import Item
from admin_web.utils.auth import admin_required


class ItemController:
    def __init__(self, db_path: str = 'economy.db'):
        self.item_service = ItemService(db_path)
        self.shop_service = ShopService(db_path)

    @admin_required
    def get_items(self):
        """GET /api/v1/items - 아이템 목록"""
        items = self.item_service.get_active_items()
        return jsonify({'items': [i.to_dict() for i in items]})

    @admin_required
    def create_item(self):
        """POST /api/v1/items - 아이템 생성"""
        data = request.get_json()
        item = Item.from_dict(data)
        
        try:
            result = self.item_service.create_item(item)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    def purchase_item(self):
        """POST /api/v1/shop/purchase - 아이템 구매"""
        data = request.get_json()
        user_id = data.get('user_id')
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        
        result = self.shop_service.purchase_item(user_id, item_id, quantity)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
