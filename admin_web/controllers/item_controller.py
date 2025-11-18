"""Item controller"""
from flask import request, jsonify
from admin_web.services.item_service import ItemService


class ItemController:
    """아이템 API 컨트롤러"""

    def __init__(self):
        self.item_service = ItemService()

    def get_items(self):
        """아이템 목록 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            is_active_str = request.args.get('is_active')
            is_active = None
            if is_active_str is not None:
                is_active = is_active_str.lower() == 'true'

            result = self.item_service.get_items(page, limit, is_active)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def create_item(self):
        """아이템 생성 API"""
        try:
            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            price = data.get('price', 0)
            is_active = data.get('is_active', True)
            admin_name = data.get('admin_name')

            if not name:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'name is required'
                    }
                }), 400

            item = self.item_service.create_item(name, description, price, is_active, admin_name)
            return jsonify(item.to_dict()), 201
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def update_item(self, item_id):
        """아이템 수정 API"""
        try:
            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            price = data.get('price', 0)
            is_active = data.get('is_active', True)
            admin_name = data.get('admin_name')

            if not name:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'name is required'
                    }
                }), 400

            success = self.item_service.update_item(item_id, name, description, price, is_active, admin_name)
            if success:
                return jsonify({'message': 'Item updated'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Item not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def delete_item(self, item_id):
        """아이템 삭제 API"""
        try:
            data = request.get_json() or {}
            admin_name = data.get('admin_name')

            success = self.item_service.delete_item(item_id, admin_name)
            if success:
                return jsonify({'message': 'Item deleted'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Item not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
