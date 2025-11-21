"""웹 UI 라우트"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from admin_web.services.user_service import UserService
from admin_web.services.item_service import ItemService
from admin_web.services.warning_service import WarningService

web_bp = Blueprint('web', __name__)

# 간단한 인메모리 인증 (실제로는 DB 사용)
# 비밀번호는 환경 변수에서 가져옴 (기본값: admin123)
def _get_admin_users():
    """환경 변수에서 관리자 사용자 정보를 가져옵니다."""
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    if admin_password == 'admin123':
        print("경고: ADMIN_PASSWORD 환경 변수가 설정되지 않았습니다. 기본 비밀번호를 사용 중입니다!")
    return {
        'admin': generate_password_hash(admin_password)
    }

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
            flash('잘못된 사용자명 또는 비밀번호', 'danger')

    return render_template('login.html')


@web_bp.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다', 'info')
    return redirect(url_for('web.login'))


@web_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('web.login'))
    
    user_service = UserService()
    item_service = ItemService()
    
    users = user_service.get_all_users()
    items = item_service.get_active_items()
    
    stats = {
        'total_users': len(users),
        'total_items': len(items),
        'total_balance': sum(u.balance for u in users),
    }
    
    return render_template('dashboard.html', stats=stats)


@web_bp.route('/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('web.login'))
    
    user_service = UserService()
    all_users = user_service.get_all_users()
    
    return render_template('users.html', users=all_users)


@web_bp.route('/items')
def items():
    if 'user_id' not in session:
        return redirect(url_for('web.login'))
    
    item_service = ItemService()
    all_items = item_service.get_active_items()
    
    return render_template('items.html', items=all_items)


@web_bp.route('/warnings')
def warnings():
    if 'user_id' not in session:
        return redirect(url_for('web.login'))
    
    return render_template('dashboard.html', stats={'total_users': 0, 'total_items': 0, 'total_balance': 0})


@web_bp.route('/calendar')
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('web.login'))
    
    return render_template('dashboard.html', stats={'total_users': 0, 'total_items': 0, 'total_balance': 0})
