"""
Auth Controller
인증 관련 비즈니스 로직
"""
from flask import redirect, url_for, session
from mastodon import Mastodon
from admin_web.services.user_service import UserService


class AuthController:
    """인증 컨트롤러"""

    def __init__(self, config):
        """
        Args:
            config: Flask app config
        """
        self.config = config
        self.user_service = UserService(config['DATABASE_PATH'])

    def get_mastodon_client(self):
        """마스토돈 클라이언트 생성"""
        return Mastodon(
            client_id=self.config['MASTODON_CLIENT_ID'],
            client_secret=self.config['MASTODON_CLIENT_SECRET'],
            api_base_url=self.config['MASTODON_INSTANCE_URL']
        )

    def login(self):
        """OAuth 로그인 시작"""
        mastodon = self.get_mastodon_client()

        # OAuth URL 생성
        auth_url = mastodon.auth_request_url(
            redirect_uris=url_for('auth.oauth_callback', _external=True),
            scopes=['read:accounts']
        )

        return redirect(auth_url)

    def oauth_callback(self, request):
        """
        OAuth 콜백 처리

        Args:
            request: Flask request 객체

        Returns:
            redirect 또는 오류 메시지
        """
        code = request.args.get('code')

        if not code:
            return "인증 코드가 없습니다.", 400

        try:
            mastodon = self.get_mastodon_client()

            # 액세스 토큰 발급
            access_token = mastodon.log_in(
                code=code,
                redirect_uri=url_for('auth.oauth_callback', _external=True),
                scopes=['read:accounts']
            )

            # 유저 정보 조회
            mastodon.access_token = access_token
            account = mastodon.account_verify_credentials()

            # 유저 생성 또는 조회
            user = self.user_service.get_or_create_user(
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

            return redirect(url_for('main.dashboard'))

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"OAuth 오류: {e}")
            return f"로그인 실패: {e}", 500

    def logout(self):
        """로그아웃"""
        session.clear()
        return redirect(url_for('main.index'))
