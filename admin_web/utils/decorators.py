"""
Utility decorators
로그인 체크, 권한 체크 등
"""
from functools import wraps
from flask import session, redirect, url_for, render_template


def login_required(f):
    """
    로그인 필수 데코레이터

    사용법:
        @login_required
        def my_view():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    관리자 권한 필수 데코레이터

    사용법:
        @admin_required
        def my_admin_view():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        if not session.get('is_admin', False):
            return render_template('error.html',
                error_title="권한 없음",
                error_message="관리자 권한이 필요합니다."
            ), 403

        return f(*args, **kwargs)
    return decorated_function
