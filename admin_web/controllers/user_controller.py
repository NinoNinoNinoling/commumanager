"""
User Controller
"""
from flask import request, jsonify
from admin_web.services.user_service import UserService


def get_user_detail(user_id):
    """
    Get details for a single user.
    """
    service = UserService()
    user = service.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()})


def update_user_role(user_id):
    """
    Update a user's role.
    """
    data = request.get_json()
    if not data or 'role' not in data:
        return jsonify({'error': 'Missing role field in request body'}), 400

    new_role = data.get('role')
    
    service = UserService()
    try:
        updated_user = service.update_user_role(user_id, new_role)
        return jsonify({'user': updated_user.to_dict()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
