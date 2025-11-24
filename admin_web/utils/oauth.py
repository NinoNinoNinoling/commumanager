"""Mastodon OAuth 인증 헬퍼"""
import os
import logging
from typing import Optional, Tuple
from mastodon import Mastodon

logger = logging.getLogger(__name__)


class MastodonOAuth:
    """Mastodon OAuth 인증 처리"""

    def __init__(self):
        self.instance_url = os.environ.get('MASTODON_INSTANCE_URL', 'https://mastodon.social')
        self.client_id = os.environ.get('MASTODON_CLIENT_ID')
        self.client_secret = os.environ.get('MASTODON_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('MASTODON_REDIRECT_URI', 'http://localhost:5000/oauth/callback')

    def register_app(self) -> Tuple[str, str]:
        """
        Mastodon 앱을 등록하고 클라이언트 ID와 시크릿을 받습니다.

        Returns:
            (client_id, client_secret) 튜플

        Note:
            실제 환경에서는 이 값들을 환경 변수에 저장해야 합니다.
        """
        try:
            client_id, client_secret = Mastodon.create_app(
                'CommuManager Admin',
                api_base_url=self.instance_url,
                redirect_uris=self.redirect_uri,
                scopes=['read', 'write', 'follow', 'push'],
                website='https://github.com/your-repo'
            )
            logger.info(f"✅ Mastodon 앱 등록 성공: {self.instance_url}")
            return client_id, client_secret
        except Exception as e:
            logger.error(f"❌ Mastodon 앱 등록 실패: {e}")
            raise

    def get_authorization_url(self) -> str:
        """
        OAuth 인증 URL을 생성합니다.

        Returns:
            사용자를 리디렉션할 인증 URL
        """
        if not self.client_id or not self.client_secret:
            logger.warning("⚠️  MASTODON_CLIENT_ID/SECRET 없음, 앱 등록 시도")
            self.client_id, self.client_secret = self.register_app()

        mastodon = Mastodon(
            client_id=self.client_id,
            client_secret=self.client_secret,
            api_base_url=self.instance_url
        )

        auth_url = mastodon.auth_request_url(
            scopes=['read', 'write', 'follow', 'push'],
            redirect_uris=self.redirect_uri
        )

        return auth_url

    def get_access_token(self, code: str) -> str:
        """
        인증 코드로 액세스 토큰을 받습니다.

        Args:
            code: OAuth 콜백에서 받은 인증 코드

        Returns:
            액세스 토큰
        """
        mastodon = Mastodon(
            client_id=self.client_id,
            client_secret=self.client_secret,
            api_base_url=self.instance_url
        )

        access_token = mastodon.log_in(
            code=code,
            redirect_uri=self.redirect_uri,
            scopes=['read', 'write', 'follow', 'push']
        )

        return access_token

    def get_user_info(self, access_token: str) -> dict:
        """
        액세스 토큰으로 사용자 정보를 가져옵니다.

        Args:
            access_token: Mastodon 액세스 토큰

        Returns:
            사용자 정보 딕셔너리
        """
        mastodon = Mastodon(
            access_token=access_token,
            api_base_url=self.instance_url
        )

        account = mastodon.account_verify_credentials()

        return {
            'id': account['id'],
            'username': account['username'],
            'acct': account['acct'],
            'display_name': account['display_name'],
            'avatar': account['avatar'],
            'url': account['url']
        }

    def verify_admin(self, access_token: str) -> bool:
        """
        사용자가 관리자 권한이 있는지 확인합니다.

        DB에서 관리자 목록을 조회하여 확인합니다.
        로컬 계정과 원격 계정을 모두 지원하며, 도메인이 있는/없는 형식 모두 매칭합니다.

        Args:
            access_token: Mastodon 액세스 토큰

        Returns:
            관리자 여부

        Note:
            oauth_admins 테이블에서 is_active=1인 관리자만 인증 허용
        """
        from admin_web.services.oauth_admin_service import OAuthAdminService

        user_info = self.get_user_info(access_token)
        user_acct = user_info['acct']  # 로컬: 'admin', 원격: 'user@remote.instance'
        user_name = user_info['username']  # 항상 도메인 없는 이름

        # 디버깅 로그
        logger.info(f"🔍 OAuth 인증 시도 - username: {user_name}, acct: {user_acct}")

        # DB에서 관리자 권한 확인
        oauth_admin_service = OAuthAdminService()
        is_admin = oauth_admin_service.is_admin(user_acct, user_name)

        if is_admin:
            logger.info(f"✅ 관리자 인증 성공: {user_acct}")
            # 마지막 로그인 시각 업데이트
            oauth_admin_service.update_last_login(user_acct)
        else:
            logger.warning(f"❌ 관리자 인증 실패 - {user_acct}는 DB에 없거나 비활성화되었습니다")

        return is_admin
