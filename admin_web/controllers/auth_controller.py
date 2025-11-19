"""
Auth Controller
인증 관련 비즈니스 로직
"""
from flask import redirect, url_for, session, current_app, render_template
from mastodon import Mastodon
from admin_web.services.user_service import UserService


class AuthController:
    """인증 컨트롤러"""

    def __init__(self):
        """초기화"""
        self.user_service = UserService()

    def get_mastodon_client(self):
        """마스토돈 클라이언트 생성"""
        return Mastodon(
            client_id=current_app.config['MASTODON_CLIENT_ID'],
            client_secret=current_app.config['MASTODON_CLIENT_SECRET'],
            api_base_url=current_app.config['MASTODON_INSTANCE_URL']
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
            return render_template('error.html',
                error_title="인증 실패",
                error_message="인증 코드가 없습니다."
            ), 400

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

            mastodon_id = str(account['id'])
            username = account['username']
            display_name = account['display_name'] or username

            # 사용자 조회 (economy.db에서)
            user = self.user_service.get_user(mastodon_id)

            if not user:
                # 사용자가 DB에 없으면 권한 없음
                return render_template('error.html',
                    error_title="권한 없음",
                    error_message="관리자 권한이 필요합니다. 먼저 economy.db에 사용자를 등록해야 합니다."
                ), 403

            # 관리자 권한 확인
            if user.role not in ['admin', 'super_admin']:
                return render_template('error.html',
                    error_title="권한 없음",
                    error_message="관리자 권한이 필요합니다. 현재 권한: " + user.role
                ), 403

            # 세션에 유저 정보 저장
            session['user_id'] = mastodon_id
            session['username'] = username
            session['display_name'] = display_name
            session['is_admin'] = True
            session['access_token'] = access_token

            return redirect(url_for('web.dashboard'))

        except Exception as e:
            current_app.logger.error(f"OAuth 오류: {e}")
            return render_template('error.html',
                error_title="로그인 실패",
                error_message=f"인증 중 오류가 발생했습니다: {str(e)}"
            ), 500

    def logout(self):
        """로그아웃"""
        session.clear()
        return redirect(url_for('auth.login'))
