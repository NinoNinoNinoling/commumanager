"""웹 UI 라우트"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from admin_web.services.user_service import UserService
from admin_web.services.item_service import ItemService
from admin_web.services.warning_service import WarningService

web_bp = Blueprint('web', __name__)

# 간단한 인메모리 인증 (실제로는 DB 사용)
ADMIN_USERS = {
    'admin': 'admin123'
}


@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ADMIN_USERS and ADMIN_USERS[username] == password:
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
