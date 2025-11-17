"""
Authentication Routes
인증 관련 라우트 (로그인, 로그아웃, OAuth 콜백)
"""
from flask import Blueprint, redirect, url_for, request, session, current_app
from admin_web.controllers.auth_controller import AuthController

# Blueprint 생성
auth_bp = Blueprint('auth', __name__)

# Controller 인스턴스 (나중에 초기화)
auth_controller = None


def init_auth_routes(app):
    """
    인증 라우트 초기화

    Args:
        app: Flask app 인스턴스
    """
    global auth_controller
    auth_controller = AuthController(app.config)


@auth_bp.route('/login')
def login():
    """OAuth 로그인 시작"""
    return auth_controller.login()


@auth_bp.route('/oauth/callback')
def oauth_callback():
    """OAuth 콜백 처리"""
    return auth_controller.oauth_callback(request)


@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    return auth_controller.logout()
