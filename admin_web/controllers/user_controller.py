"""UserController"""
from flask import request, jsonify
from admin_web.services.user_service import UserService
from admin_web.utils.auth import admin_required


class UserController:
    """
    유저 관리 API 요청을 처리하는 Controller

    유저 조회, 잔액 조정 등 유저 관련 API 엔드포인트의 요청을 처리하고
    UserService를 호출하여 비즈니스 로직을 실행합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        self.user_service = UserService(db_path)

    @admin_required
    def get_users(self):
        """GET /api/v1/users - 유저 목록"""
        users = self.user_service.get_all_users()
        return jsonify({'users': [u.to_dict() for u in users]})

    @admin_required
    def get_user(self, user_id: str):
        """GET /api/v1/users/:id - 유저 상세"""
        user = self.user_service.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': user.to_dict()})

    @admin_required
    def adjust_balance(self, user_id: str):
        """POST /api/v1/users/:id/balance - 잔액 조정"""
        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description', '관리자 조정')
        
        try:
            result = self.user_service.adjust_balance(user_id, amount, 'adjustment', description, 'admin')
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
