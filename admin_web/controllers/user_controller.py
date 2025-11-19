"""User controller"""
from flask import request, jsonify
from admin_web.services.user_service import UserService
from admin_web.repositories.transaction_repository import TransactionRepository


class UserController:
    """유저 API 컨트롤러"""

    def __init__(self):
        self.user_service = UserService()
        self.transaction_repo = TransactionRepository()

    def get_users(self):
        """유저 목록 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            search = request.args.get('search')
            role = request.args.get('role')
            sort = request.args.get('sort', 'created_desc')

            result = self.user_service.get_users(page, limit, search, role, sort)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def get_user(self, mastodon_id):
        """유저 상세 조회 API"""
        try:
            user_detail = self.user_service.get_user_detail(mastodon_id)
            if not user_detail:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'User not found'
                    }
                }), 404

            return jsonify(user_detail), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def update_role(self, mastodon_id):
        """역할 변경 API"""
        try:
            data = request.get_json()
            new_role = data.get('role')

            if not new_role:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'role is required'
                    }
                }), 400

            success = self.user_service.change_role(mastodon_id, new_role)
            if success:
                return jsonify({'message': 'Role updated'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'User not found'
                    }
                }), 404
        except ValueError as e:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': str(e)
                }
            }), 400
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def adjust_balance(self):
        """재화 조정 API"""
        try:
            data = request.get_json()
            mastodon_id = data.get('user_id')
            amount = data.get('amount')
            description = data.get('description', '')
            admin_name = data.get('admin_name')

            if not mastodon_id or amount is None:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'user_id and amount are required'
                    }
                }), 400

            success = self.user_service.adjust_balance(mastodon_id, amount, description, admin_name)
            if success:
                return jsonify({'message': 'Balance adjusted'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'User not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def get_transactions(self, mastodon_id):
        """유저별 거래 내역 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            transaction_type = request.args.get('type')

            transactions, total = self.transaction_repo.find_by_user(
                mastodon_id, page, limit, transaction_type
            )
            total_pages = (total + limit - 1) // limit

            return jsonify({
                'transactions': [t.to_dict() for t in transactions],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': total_pages,
                }
            }), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
