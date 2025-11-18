"""
Authentication Routes
인증 관련 라우트 (로그인, 로그아웃, OAuth 콜백)
"""
from flask import Blueprint, redirect, url_for, request, session, current_app, render_template
from admin_web.controllers.auth_controller import AuthController

# Blueprint 생성
auth_bp = Blueprint('auth', __name__)


def get_auth_controller():
    """Auth 컨트롤러 인스턴스 가져오기"""
    return AuthController()


@auth_bp.route('/login')
def login():
    """OAuth 로그인 시작 또는 로그인 페이지"""
    # 이미 로그인 되어 있으면 대시보드로
    if 'user_id' in session:
        return redirect(url_for('web.dashboard'))

    return render_template('login.html')


@auth_bp.route('/oauth/start')
def oauth_start():
    """OAuth 인증 시작"""
    return get_auth_controller().login()


@auth_bp.route('/oauth/callback')
def oauth_callback():
    """OAuth 콜백 처리"""
    return get_auth_controller().oauth_callback(request)


@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    return get_auth_controller().logout()
