"""인증 & 권한 유틸리티"""
from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다', 'error')
            return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """관리자 권한 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다', 'error')
            return redirect(url_for('web.login'))
        if session.get('role') != 'admin':
            flash('관리자 권한이 필요합니다', 'error')
            return redirect(url_for('web.index'))
        return f(*args, **kwargs)
    return decorated_function


def check_permission(user_role: str, required_role: str) -> bool:
    """권한 체크"""
    role_hierarchy = {'admin': 3, 'moderator': 2, 'user': 1, 'guest': 0}
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
