"""
Warning Controller
"""
from flask import request, jsonify
from admin_web.services.warning_service import WarningService

def create_warning():
    """
    Manually issue a warning to a user.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    user_id = data.get('user_id')
    warning_type = data.get('warning_type')
    message = data.get('message')
    admin_name = data.get('admin_name')

    if not all([user_id, warning_type, message, admin_name]):
        return jsonify({'error': 'Missing required fields: user_id, warning_type, message, admin_name'}), 400

    try:
        service = WarningService()
        result = service.issue_warning(
            user_id=user_id,
            warning_type=warning_type,
            message=message,
            admin_name=admin_name
        )
        # Convert models to dicts for JSON serialization
        result['warning'] = result['warning'].to_dict()
        result['user'] = result['user'].to_dict()
        
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
