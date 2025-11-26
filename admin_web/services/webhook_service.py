"""
WebhookService

마스토돈 웹훅 이벤트를 처리하는 비즈니스 로직
"""
import logging
from typing import Dict, Any, Optional

from admin_web.models.user import User
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository


logger = logging.getLogger(__name__)


class WebhookService:
    """
    마스토돈 웹훅 이벤트 처리를 위한 Service

    처리 내용:
    - account.created: 새 유저를 DB에 자동 등록
    - 역할 정보 동기화 (role_name, role_color)
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        WebhookService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.user_repo = UserRepository(db_path)
        self.admin_log_repo = AdminLogRepository(db_path)
        self.db_path = db_path

    def handle_account_created(self, webhook_data: dict) -> Dict[str, Any]:
        """
        account.created 웹훅 이벤트를 처리합니다.

        새 계정이 생성되면 DB에 유저를 자동으로 등록합니다.
        이미 존재하는 경우 역할 정보만 업데이트합니다.

        Args:
            webhook_data: 마스토돈 웹훅 페이로드

        Returns:
            처리 결과 딕셔너리

        Raises:
            ValueError: 필수 필드가 없거나 유효하지 않은 경우
        """
        # 페이로드 파싱
        obj = webhook_data.get('object')
        if not obj:
            raise ValueError("웹훅 페이로드에 'object' 필드가 없습니다")

        mastodon_id = obj.get('id')
        username = obj.get('username')
        acct = obj.get('acct')
        display_name = obj.get('display_name') or username

        if not mastodon_id or not username:
            raise ValueError("필수 필드가 없습니다: id, username")

        # 역할 정보 추출 (있는 경우)
        role_name = None
        role_color = None
        role_obj = obj.get('role')
        if role_obj:
            role_name = role_obj.get('name')
            role_color = role_obj.get('color')

        logger.info(f"계정 생성 이벤트: @{acct} (ID: {mastodon_id})")

        # 기존 유저 확인
        existing_user = self.user_repo.find_by_id(mastodon_id)

        if existing_user:
            logger.info(f"이미 존재하는 유저: {mastodon_id}, 역할 정보만 업데이트")

            # 역할 정보 업데이트
            if role_name or role_color:
                self.user_repo.update_role_info(
                    mastodon_id=mastodon_id,
                    role_name=role_name,
                    role_color=role_color
                )

            return {
                'status': 'updated',
                'user_id': mastodon_id,
                'username': username,
                'message': '역할 정보 업데이트됨'
            }

        # 새 유저 생성
        new_user = User(
            mastodon_id=mastodon_id,
            username=username,
            display_name=display_name,
            role='user',  # 기본 역할
            balance=0,  # 초기 재화 지급 안 함 (사용자 요청)
            total_earned=0,
            total_spent=0,
            reply_count=0,
            warning_count=0,
            is_key_member=False,
            role_name=role_name,
            role_color=role_color
        )

        created_user = self.user_repo.create(new_user)

        # 관리 로그 기록
        self.admin_log_repo.create_log(
            action_type='webhook_account_created',
            admin_name='system',
            target_user=mastodon_id,
            description=f'웹훅으로 새 유저 등록: @{acct}',
            details={
                'username': username,
                'display_name': display_name,
                'role_name': role_name,
                'role_color': role_color
            }
        )

        logger.info(f"새 유저 등록 완료: @{acct} (ID: {mastodon_id})")

        return {
            'status': 'created',
            'user_id': created_user.mastodon_id,
            'username': created_user.username,
            'display_name': created_user.display_name,
            'balance': created_user.balance,
            'message': '새 유저가 등록되었습니다'
        }

    def update_user_role(self, mastodon_id: str, role_name: Optional[str],
                         role_color: Optional[str]) -> Dict[str, Any]:
        """
        유저의 마스토돈 역할 정보를 업데이트합니다.

        Args:
            mastodon_id: 유저의 Mastodon ID
            role_name: 마스토돈 역할 이름
            role_color: 마스토돈 역할 색상

        Returns:
            업데이트 결과 딕셔너리

        Raises:
            ValueError: 유저를 찾을 수 없는 경우
        """
        user = self.user_repo.find_by_id(mastodon_id)
        if not user:
            raise ValueError(f'유저를 찾을 수 없습니다: {mastodon_id}')

        self.user_repo.update_role_info(
            mastodon_id=mastodon_id,
            role_name=role_name,
            role_color=role_color
        )

        # 관리 로그 기록
        self.admin_log_repo.create_log(
            action_type='webhook_role_updated',
            admin_name='system',
            target_user=mastodon_id,
            description=f'역할 정보 업데이트: {role_name}',
            details={
                'role_name': role_name,
                'role_color': role_color
            }
        )

        logger.info(f"역할 업데이트 완료: {mastodon_id} → {role_name}")

        return {
            'status': 'updated',
            'user_id': mastodon_id,
            'role_name': role_name,
            'role_color': role_color,
            'message': '역할 정보가 업데이트되었습니다'
        }
