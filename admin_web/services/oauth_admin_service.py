"""
OAuthAdminService

OAuth 관리자 비즈니스 로직 처리
"""
from typing import List, Optional
from datetime import datetime

from admin_web.models.oauth_admin import OAuthAdmin
from admin_web.repositories.oauth_admin_repository import OAuthAdminRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository


class OAuthAdminService:
    """
    OAuth 관리자 관리 비즈니스 로직을 처리하는 서비스

    관리자 추가, 제거, 활성화/비활성화 등의 작업을 수행합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        OAuthAdminService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.oauth_admin_repo = OAuthAdminRepository(db_path)
        self.admin_log_repo = AdminLogRepository(db_path)

    def is_admin(self, mastodon_acct: str, username: str = None) -> bool:
        """
        주어진 계정이 활성화된 관리자인지 확인합니다.

        로컬 계정과 원격 계정을 모두 지원하며, 도메인이 있는/없는 형식 모두 매칭합니다.

        Args:
            mastodon_acct: Mastodon 계정 (acct 필드, 예: 'admin' 또는 'user@remote.instance')
            username: Mastodon 계정 이름 (도메인 없음, 예: 'admin')

        Returns:
            활성화된 관리자이면 True, 아니면 False

        Note:
            - acct 기준 정확히 일치
            - username 기준 일치
            - DB의 계정에서 도메인을 제거한 것과 일치
        """
        # 1. acct 기준 정확히 일치하는 경우
        if self.oauth_admin_repo.is_admin(mastodon_acct):
            return True

        # 2. username이 제공된 경우, username 기준 일치
        if username and self.oauth_admin_repo.is_admin(username):
            return True

        # 3. DB의 모든 활성화된 관리자 중에서 도메인 제외 매칭
        active_admins = self.oauth_admin_repo.find_active()
        for admin in active_admins:
            admin_acct = admin.mastodon_acct

            # DB 계정에 '@'가 있으면 도메인 제거하고 비교
            if '@' in admin_acct:
                admin_name_only = admin_acct.split('@')[0]
                if mastodon_acct == admin_name_only or (username and username == admin_name_only):
                    return True

        return False

    def get_all_admins(self) -> List[OAuthAdmin]:
        """
        모든 OAuth 관리자를 조회합니다.

        Returns:
            OAuthAdmin 리스트
        """
        return self.oauth_admin_repo.find_all()

    def get_active_admins(self) -> List[OAuthAdmin]:
        """
        활성화된 OAuth 관리자만 조회합니다.

        Returns:
            활성화된 OAuthAdmin 리스트
        """
        return self.oauth_admin_repo.find_active()

    def add_admin(
        self,
        mastodon_acct: str,
        added_by: str,
        display_name: Optional[str] = None
    ) -> OAuthAdmin:
        """
        새로운 OAuth 관리자를 추가합니다.

        Args:
            mastodon_acct: Mastodon 계정
            added_by: 추가한 관리자 이름
            display_name: 표시 이름 (선택)

        Returns:
            생성된 OAuthAdmin 객체

        Raises:
            ValueError: 이미 존재하는 계정인 경우
        """
        existing = self.oauth_admin_repo.find_by_acct(mastodon_acct)
        if existing:
            raise ValueError(f'이미 등록된 관리자 계정입니다: {mastodon_acct}')

        admin = OAuthAdmin(
            mastodon_acct=mastodon_acct,
            display_name=display_name,
            added_by=added_by,
            is_active=True
        )

        created = self.oauth_admin_repo.create(admin)

        self.admin_log_repo.create_log(
            action_type='oauth_admin_add',
            admin_name=added_by,
            target_user=mastodon_acct,
            details={'display_name': display_name, 'success': True}
        )

        return created

    def remove_admin(self, mastodon_acct: str, removed_by: str) -> bool:
        """
        OAuth 관리자를 삭제합니다.

        Args:
            mastodon_acct: Mastodon 계정
            removed_by: 삭제한 관리자 이름

        Returns:
            삭제 성공 여부
        """
        success = self.oauth_admin_repo.delete(mastodon_acct)

        if success:
            self.admin_log_repo.create_log(
                action_type='oauth_admin_remove',
                admin_name=removed_by,
                target_user=mastodon_acct,
                details={'success': True}
            )

        return success

    def deactivate_admin(self, mastodon_acct: str, deactivated_by: str) -> bool:
        """
        OAuth 관리자를 비활성화합니다.

        Args:
            mastodon_acct: Mastodon 계정
            deactivated_by: 비활성화한 관리자 이름

        Returns:
            비활성화 성공 여부
        """
        success = self.oauth_admin_repo.deactivate(mastodon_acct)

        if success:
            self.admin_log_repo.create_log(
                action_type='oauth_admin_deactivate',
                admin_name=deactivated_by,
                target_user=mastodon_acct,
                details={'success': True}
            )

        return success

    def activate_admin(self, mastodon_acct: str, activated_by: str) -> bool:
        """
        OAuth 관리자를 활성화합니다.

        Args:
            mastodon_acct: Mastodon 계정
            activated_by: 활성화한 관리자 이름

        Returns:
            활성화 성공 여부
        """
        success = self.oauth_admin_repo.activate(mastodon_acct)

        if success:
            self.admin_log_repo.create_log(
                action_type='oauth_admin_activate',
                admin_name=activated_by,
                target_user=mastodon_acct,
                details={'success': True}
            )

        return success

    def update_last_login(self, mastodon_acct: str) -> bool:
        """
        마지막 로그인 시각을 업데이트합니다.

        Args:
            mastodon_acct: Mastodon 계정

        Returns:
            업데이트 성공 여부
        """
        return self.oauth_admin_repo.update_last_login(mastodon_acct, datetime.now())
