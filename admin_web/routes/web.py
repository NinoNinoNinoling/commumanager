"""웹 UI 라우트"""
import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from admin_web.services.user_service import UserService
from admin_web.services.item_service import ItemService
from admin_web.services.transaction_service import TransactionService
from admin_web.services.vacation_service import VacationService
from admin_web.services.warning_service import WarningService
from admin_web.services.moderation_service import ModerationService # 사용하지 않더라도 초기화 충돌 방지
from admin_web.utils.auth import login_required
from admin_web.utils.oauth import MastodonOAuth

# 🆕 Blueprint 이름 변경: 'web' 대신 'web_bp' 사용
web_bp = Blueprint('web', __name__) 
logger = logging.getLogger(__name__)

# 전역 서비스 인스턴스는 제거 (사용자님의 이전 코드 스타일이 혼재되어 있어 제거)
# 라우트 내에서 서비스 인스턴스화 하거나, app.py에서 주입해야 함

def _get_admin_users():
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    if admin_password == 'admin123':
        logger.warning("⚠️ ADMIN_PASSWORD 미설정: 기본값 사용 중")
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


# 🚨 주의: web.py가 복구되면서 아래 라우트들이 복잡하게 섞여 있었는데, 
# app.py에서 web_bp만 임포트하고 라우트 함수 이름에 @web_bp.route 데코레이터가 붙어있다면 실행에 문제는 없습니다.
# 여기서는 라우트만 남기고 불필요한 전역 변수 초기화는 제거하여 안정성을 확보합니다.

@web_bp.route('/')
@login_required
def index():
    from admin_web.services.dashboard_service import DashboardService
    return render_template('dashboard.html', stats=DashboardService().get_dashboard_stats())

@web_bp.route('/users')
@login_required
def users():
    user_service = UserService()
    all_users = user_service.get_all_users()
    
    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
    return render_template('users.html', users=all_users, mastodon_url=mastodon_url)

@web_bp.route('/users/<user_id>')
@login_required
def user_detail(user_id):
    user_service = UserService()
    transaction_service = TransactionService()
    vacation_service = VacationService()
    warning_service = WarningService()
    
    user = user_service.get_user(user_id)
    if not user:
        flash('존재하지 않는 유저입니다.', 'danger')
        return redirect(url_for('web.users'))
        
    transactions = transaction_service.get_user_transactions(user_id)
    is_on_vacation = vacation_service.is_user_on_vacation(user_id)
    warnings_history = warning_service.get_user_warnings(user_id) # ⬅️ 이 데이터가 사용되지 않지만, 오류를 피하기 위해 유지

    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
    
    return render_template('user_detail.html', 
                           user=user, 
                           transactions=transactions, 
                           mastodon_url=mastodon_url,
                           is_on_vacation=is_on_vacation,
                           warnings=warnings_history) # ⬅️ warnings_history 대신 warnings로 템플릿에 전달해야 HTML 롤백이 가능함

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
    mastodon_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
    mastodon_settings_url = f"{mastodon_url}/settings/profile"

    return render_template('account.html',
                           mastodon_url=mastodon_url,
                           mastodon_settings_url=mastodon_settings_url)
