"""웹 UI 라우트"""
import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from admin_web.utils.auth import login_required
from admin_web.utils.oauth import MastodonOAuth

# Dependencies (DI 적용)
from admin_web.dependencies import (
    get_user_service,
    get_item_service,
    get_transaction_service,
    get_vacation_service,
    get_warning_service,
    get_settings_service,
    get_dashboard_service
)

web_bp = Blueprint('web', __name__)
logger = logging.getLogger(__name__)

def _get_admin_users():
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_password:
        # 개발 편의를 위해 경고만 하고 넘어갈 수도 있지만, 프로덕션 안전을 위해 에러 유지
        if os.environ.get('FLASK_ENV') == 'development':
            return {'admin': generate_password_hash('admin')}
        raise RuntimeError("ADMIN_PASSWORD 환경 변수가 설정되지 않았습니다.")
    return {'admin': generate_password_hash(admin_password)}

ADMIN_USERS = _get_admin_users()

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in ADMIN_USERS and check_password_hash(ADMIN_USERS[username], password):
            session['user_id'] = username
            session['role'] = 'admin'
            flash('로그인 성공!', 'success')
            return redirect(url_for('web.index'))
        else:
            flash('잘못된 정보', 'danger')
    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
    return render_template('login.html', mastodon_url=mastodon_url)

@web_bp.route('/oauth/login')
def oauth_login():
    try:
        return redirect(MastodonOAuth().get_authorization_url())
    except Exception as e:
        flash(f'OAuth 실패: {e}', 'danger')
        return redirect(url_for('web.login'))

@web_bp.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    if not code: return redirect(url_for('web.login'))
    try:
        oauth = MastodonOAuth()
        token = oauth.get_access_token(code)
        user_info = oauth.get_user_info(token)
        if not oauth.verify_admin(token):
            flash('관리자 권한 없음', 'danger')
            return redirect(url_for('web.login'))
        
        session['user_id'] = user_info['acct']
        session['username'] = user_info['username']
        session['role'] = 'admin'
        return redirect(url_for('web.index'))
    except Exception as e:
        flash(f'인증 에러: {e}', 'danger')
        return redirect(url_for('web.login'))

@web_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('web.login'))


@web_bp.route('/')
@login_required
def index():
    dashboard_service = get_dashboard_service()
    return render_template('dashboard.html', stats=dashboard_service.get_dashboard_stats())

@web_bp.route('/users')
@login_required
def users():
    user_service = get_user_service()
    all_users = user_service.get_all_users()
    
    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
    return render_template('users.html', users=all_users, mastodon_url=mastodon_url)

@web_bp.route('/users/<user_id>')
@login_required
def user_detail(user_id):
    user_service = get_user_service()
    transaction_service = get_transaction_service()
    vacation_service = get_vacation_service()
    warning_service = get_warning_service()
    
    user = user_service.get_user(user_id)
    if not user:
        flash('존재하지 않는 유저입니다.', 'danger')
        return redirect(url_for('web.users'))
        
    transactions = transaction_service.get_user_transactions(user_id)
    is_on_vacation = vacation_service.is_user_on_vacation(user_id)
    warnings_history = warning_service.get_user_warnings(user_id)

    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')

    return render_template('user_detail.html',
                           user=user,
                           transactions=transactions,
                           mastodon_url=mastodon_url,
                           is_on_vacation=is_on_vacation,
                           warnings=warnings_history)

@web_bp.route('/items')
@login_required
def items():
    item_service = get_item_service()
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
    settings_service = get_settings_service()
    all_settings_list = settings_service.get_all_settings()
    
    # Convert list of dicts to a single dict for easier template access
    settings_dict = {setting['key']: setting['value'] for setting in all_settings_list}
    
    return render_template('settings.html', settings=settings_dict)

@web_bp.route('/account')
@login_required
def account():
    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
    mastodon_settings_url = f"{mastodon_url}/settings/profile"

    return render_template('account.html',
                           mastodon_url=mastodon_url,
                           mastodon_settings_url=mastodon_settings_url)
