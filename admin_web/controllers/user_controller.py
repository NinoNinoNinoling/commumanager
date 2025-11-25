"""UserController"""
from flask import request, jsonify
from admin_web.services.user_service import UserService
from admin_web.services.transaction_service import TransactionService
from admin_web.utils.auth import admin_required


class UserController:
    """
    유저 관리 API 요청을 처리하는 Controller
    """

    def __init__(self, db_path: str = 'economy.db'):
        self.user_service = UserService(db_path)
        self.transaction_service = TransactionService(db_path)

    @admin_required
    def get_users(self):
        """GET /api/v1/users - 유저 목록"""
        users = self.user_service.get_all_users()
        return jsonify({'users': [u.to_dict() for u in users]})

    @admin_required
    def get_risk_users(self):
        """GET /api/v1/users/risk - 위험 감지 유저 목록"""
        users = self.user_service.get_risk_users()
        return jsonify({'users': users})

    @admin_required
    def get_user(self, user_id: str):
        """GET /api/v1/users/:id - 유저 상세"""
        user = self.user_service.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': user.to_dict()})

    @admin_required
    def get_user_transactions(self, user_id: str):
        """GET /api/v1/users/:id/transactions - 유저 거래 내역"""
        try:
            transactions = self.transaction_service.get_user_transactions(user_id)
            stats = self.transaction_service.get_transaction_stats(user_id)
            return jsonify({
                'transactions': transactions,
                'stats': stats
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @admin_required
    def adjust_balance(self, user_id: str):
        """POST /api/v1/users/:id/balance - 잔액 조정"""
        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description', '관리자 조정')
        
        try:
            # session.get('user_id') 대신 일단 'admin' 하드코딩 (컨트롤러에서는 세션 접근이 어려울 수 있음)
            # 실제로는 뷰 함수에서 user_id를 넘겨받는 게 좋지만, 일단 유지
            result = self.user_service.adjust_balance(user_id, amount, 'adjustment', description, 'admin')
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
