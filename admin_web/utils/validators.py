"""
요청 데이터 검증 유틸리티
"""
from functools import wraps
from flask import request, jsonify

def validate_schema(required_fields=None):
    """
    JSON 요청 바디에 필수 필드가 있는지 검증하는 데코레이터
    
    Args:
        required_fields (list): 필수 필드 목록 (예: ['amount', 'description'])
    """
    if required_fields is None:
        required_fields = []

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. JSON 바디 확인
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Empty JSON body'}), 400

            # 2. 필수 필드 누락 확인
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'fields': missing_fields
                }), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator
