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

        Args:
            access_token: Mastodon 액세스 토큰

        Returns:
            관리자 여부
        """
        user_info = self.get_user_info(access_token)

        # 환경 변수에서 관리자 계정 목록 가져오기
        admin_accounts = os.environ.get('MASTODON_ADMIN_ACCOUNTS', '').split(',')
        admin_accounts = [acc.strip() for acc in admin_accounts if acc.strip()]

        # acct 또는 username으로 확인
        is_admin = (
            user_info['acct'] in admin_accounts or
            user_info['username'] in admin_accounts
        )

        return is_admin
