"""
마녀봇 관리자 웹 애플리케이션
Flask + Mastodon OAuth + Bootstrap 5
"""
import os
from flask import Flask, render_template, redirect, url_for, session, request
from mastodon import Mastodon
from dotenv import load_dotenv
from admin_web.config import config
from admin_web.services.user_service import UserService

# 환경 변수 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

# User Service 초기화
user_service = UserService(app.config['DATABASE_PATH'])


def get_mastodon_client():
    """마스토돈 클라이언트 생성"""
    return Mastodon(
        client_id=app.config['MASTODON_CLIENT_ID'],
        client_secret=app.config['MASTODON_CLIENT_SECRET'],
        api_base_url=app.config['MASTODON_INSTANCE_URL']
    )


# ============================================================================
# 인증 (Authentication)
# ============================================================================

@app.route('/login')
def login():
    """OAuth 로그인 시작"""
    mastodon = get_mastodon_client()

    # OAuth URL 생성
    auth_url = mastodon.auth_request_url(
        redirect_uris=url_for('oauth_callback', _external=True),
        scopes=['read:accounts']
    )

    return redirect(auth_url)


@app.route('/oauth/callback')
def oauth_callback():
    """OAuth 콜백 처리"""
    code = request.args.get('code')

    if not code:
        return "인증 코드가 없습니다.", 400

    try:
        mastodon = get_mastodon_client()

        # 액세스 토큰 발급
        access_token = mastodon.log_in(
            code=code,
            redirect_uri=url_for('oauth_callback', _external=True),
            scopes=['read:accounts']
        )

        # 유저 정보 조회
        mastodon.access_token = access_token
        account = mastodon.account_verify_credentials()

        # 유저 생성 또는 조회
        user = user_service.get_or_create_user(
            mastodon_id=str(account['id']),
            username=account['username'],
            display_name=account['display_name'] or account['username'],
            is_admin=False  # 처음에는 일반 유저로 생성
        )

        # 세션에 유저 정보 저장
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['display_name'] = user['display_name']
        session['is_admin'] = user['is_admin']
        session['access_token'] = access_token

        return redirect(url_for('dashboard'))

    except Exception as e:
        app.logger.error(f"OAuth 오류: {e}")
        return f"로그인 실패: {e}", 500


@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    return redirect(url_for('index'))


# ============================================================================
# 페이지 라우트
# ============================================================================

@app.route('/')
def index():
    """인덱스 페이지"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """대시보드 (로그인 필수)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # 관리자 권한 확인
    if not session.get('is_admin', False):
        return "관리자 권한이 필요합니다.", 403

    # 기본 통계 조회
    stats = user_service.get_user_statistics()

    return render_template('dashboard.html', stats=stats)


# ============================================================================
# 오류 핸들러
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 오류 핸들러"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 오류 핸들러"""
    app.logger.error(f"서버 오류: {error}")
    return render_template('errors/500.html'), 500


# ============================================================================
# 애플리케이션 실행
# ============================================================================

if __name__ == '__main__':
    # DB 초기화 확인
    db_path = app.config['DATABASE_PATH']
    if not os.path.exists(db_path):
        print(f"⚠️  데이터베이스가 없습니다: {db_path}")
        print(f"   다음 명령어로 초기화하세요: python init_db.py {db_path}")
        exit(1)

    print("=" * 60)
    print("마녀봇 관리자 웹 서버 시작")
    print("=" * 60)
    print(f"환경: {app.config['DEBUG'] and 'development' or 'production'}")
    print(f"DB: {db_path}")
    print(f"마스토돈: {app.config['MASTODON_INSTANCE_URL']}")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
