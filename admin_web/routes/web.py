"""웹 UI 라우트"""
import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from admin_web.services.user_service import UserService
from admin_web.services.item_service import ItemService
from admin_web.services.warning_service import WarningService
from admin_web.utils.auth import login_required
from admin_web.utils.oauth import MastodonOAuth

web_bp = Blueprint('web', __name__)
logger = logging.getLogger(__name__)

# 간단한 인메모리 인증 (실제로는 DB 사용)
# 비밀번호는 환경 변수에서 가져옴 (기본값: admin123)
def _get_admin_users():
    """환경 변수에서 관리자 사용자 정보를 가져옵니다."""
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    if admin_password == 'admin123':
        logger.warning(
            "⚠️  ADMIN_PASSWORD 환경 변수가 설정되지 않았습니다! "
            "기본 비밀번호 'admin123'을 사용 중입니다. "
            "프로덕션 환경에서는 반드시 강력한 비밀번호로 변경하세요!"
        )
    return {
        'admin': generate_password_hash(admin_password)
    }

ADMIN_USERS = _get_admin_users()


@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지 (기본 인증 + OAuth 선택)"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in ADMIN_USERS and check_password_hash(ADMIN_USERS[username], password):
            session['user_id'] = username
            session['role'] = 'admin'
            session['auth_method'] = 'basic'
            flash('로그인 성공!', 'success')
            return redirect(url_for('web.index'))
        else:
            flash('잘못된 사용자명 또는 비밀번호', 'danger')

    # Mastodon 인스턴스 URL을 템플릿에 전달
    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
    return render_template('login.html', mastodon_url=mastodon_url)


@web_bp.route('/oauth/login')
def oauth_login():
    """Mastodon OAuth 로그인 시작"""
    try:
        oauth = MastodonOAuth()
        auth_url = oauth.get_authorization_url()
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"OAuth 로그인 실패: {e}")
        flash(f'OAuth 인증 실패: {str(e)}', 'danger')
        return redirect(url_for('web.login'))


@web_bp.route('/oauth/callback')
def oauth_callback():
    """Mastodon OAuth 콜백"""
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        flash(f'OAuth 인증 거부: {error}', 'danger')
        return redirect(url_for('web.login'))

    if not code:
        flash('인증 코드가 없습니다', 'danger')
        return redirect(url_for('web.login'))

    try:
        oauth = MastodonOAuth()

        # 액세스 토큰 받기
        access_token = oauth.get_access_token(code)
        logger.info("✅ OAuth 액세스 토큰 받기 성공")

        # 사용자 정보 가져오기
        user_info = oauth.get_user_info(access_token)
        logger.info(f"✅ 사용자 정보 받기 성공: {user_info['username']} ({user_info['acct']})")

        # 관리자 권한 확인
        is_admin = oauth.verify_admin(access_token)

        if not is_admin:
            logger.warning(f"❌ 관리자 권한 없음: {user_info['acct']}")
            flash('관리자 권한이 없습니다', 'danger')
            return redirect(url_for('web.login'))

        # 세션에 저장
        session['user_id'] = user_info['acct']
        session['username'] = user_info['username']
        session['display_name'] = user_info['display_name']
        session['avatar'] = user_info['avatar']
        session['mastodon_url'] = user_info['url']
        session['access_token'] = access_token
        session['role'] = 'admin'
        session['auth_method'] = 'oauth'

        flash(f'환영합니다, {user_info["display_name"]}!', 'success')
        return redirect(url_for('web.index'))

    except Exception as e:
        logger.error(f"OAuth 콜백 처리 실패: {e}")
        flash(f'OAuth 인증 처리 실패: {str(e)}', 'danger')
        return redirect(url_for('web.login'))


@web_bp.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다', 'info')
    return redirect(url_for('web.login'))


@web_bp.route('/')
@login_required
def index():
    user_service = UserService()
    item_service = ItemService()

    all_users = user_service.get_all_users()
    items = item_service.get_active_items()

    # 시스템 계정 필터링 (마스토돈 역할 기준)
    # 일반 유저는 role_name이 None 또는 빈 문자열("")입니다
    SYSTEM_ROLES = {'Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트'}
    regular_users = [
        u for u in all_users
        if (not u.role_name) or (u.role_name.strip() not in SYSTEM_ROLES)
    ]

    stats = {
        'total_users': len(regular_users),
        'total_items': len(items),
        'total_balance': sum(u.balance for u in regular_users),
    }

    return render_template('dashboard.html', stats=stats)


@web_bp.route('/users')
@login_required
def users():
    user_service = UserService()
    all_users = user_service.get_all_users()

    return render_template('users.html', users=all_users)


@web_bp.route('/items')
@login_required
def items():
    item_service = ItemService()
    all_items = item_service.get_all_items()

    return render_template('items.html', items=all_items)


@web_bp.route('/content')
@login_required
def content():
    return render_template('content.html')


@web_bp.route('/logs')
@login_required
def logs():
    return render_template('logs.html')


@web_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@web_bp.route('/account')
@login_required
def account():
    """계정 설정 페이지"""
    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
    mastodon_settings_url = f"{mastodon_url}/settings/profile"

    return render_template('account.html',
                          mastodon_url=mastodon_url,
                          mastodon_settings_url=mastodon_settings_url)
