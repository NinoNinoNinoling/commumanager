"""WarningService

Warning 관련 비즈니스 로직을 처리하는 서비스 계층
"""
import os
from typing import List, Optional, Dict, Any
from flask import current_app

from admin_web.models.warning import Warning
from admin_web.models.ban_record import BanRecord
from admin_web.repositories.warning_repository import WarningRepository
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.ban_record_repository import BanRecordRepository
from bot.utils import create_mastodon_client, send_dm


class WarningService:
    """
    Warning 비즈니스 로직을 처리하는 Service
    """

    # 유효한 경고 유형 정의
    VALID_WARNING_TYPES = ['activity', 'isolation', 'bias', 'avoidance']

    # 자동 아웃 위험 기준 (경고 횟수)
    AT_RISK_THRESHOLD = 2

    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = current_app.config.get('DATABASE_PATH', 'economy.db')
        else:
            self.db_path = db_path
            
        self.warning_repo = WarningRepository(self.db_path)
        self.user_repo = UserRepository(self.db_path)

    def create_warning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        API 요청 데이터로부터 경고를 생성합니다. (issue_warning의 래퍼)
        """
        user_id = data.get('user_id')
        warning_type = data.get('type')  # API에서는 'type'으로 옴
        message = data.get('message')
        admin_name = data.get('admin_name', 'system')
        
        # 선택적 필드
        check_period = data.get('check_period')
        required_replies = data.get('required_replies')
        actual_replies = data.get('actual_replies')

        if not user_id or not warning_type or not message:
            raise ValueError("필수 필드가 누락되었습니다 (user_id, type, message)")

        return self.issue_warning(
            user_id=user_id,
            warning_type=warning_type,
            message=message,
            admin_name=admin_name,
            check_period_hours=check_period,
            required_replies=required_replies,
            actual_replies=actual_replies
        )

    def issue_warning(
        self,
        user_id: str,
        warning_type: str,
        message: str,
        admin_name: str,
        check_period_hours: Optional[int] = None,
        required_replies: Optional[int] = None,
        actual_replies: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        유저에게 경고를 발행하고 warning_count를 증가시킵니다.
        3회 경고 시 자동으로 아웃 처리합니다.
        """
        if warning_type not in self.VALID_WARNING_TYPES:
            raise ValueError(f'Invalid warning type: {warning_type}')

        warning = Warning(
            user_id=user_id,
            warning_type=warning_type,
            check_period_hours=check_period_hours,
            required_replies=required_replies,
            actual_replies=actual_replies,
            message=message,
            dm_sent=False,
            admin_name=admin_name
        )

        # 1. Warning 생성 및 User warning_count 증가
        created_warning = self.warning_repo.create(warning)
        self.user_repo.increment_warning_count(user_id)
        updated_user = self.user_repo.find_by_id(user_id)

        # 2. 3회 도달 시 자동 아웃 처리
        if updated_user and updated_user.warning_count >= 3:
            self._handle_auto_ban(user_id, updated_user)

        return {
            'warning': created_warning.to_dict() if hasattr(created_warning, 'to_dict') else created_warning,
            'user': updated_user.to_dict() if updated_user else None
        }

    def _handle_auto_ban(self, user_id: str, user_obj):
        """자동 아웃 처리 로직 분리"""
        ban_repo = BanRecordRepository(self.db_path)
        
        # 이미 활성 아웃 상태인지 확인
        if not ban_repo.find_active_ban(user_id):
            ban_reason = "자동 아웃: 경고 3회 누적"
            ban_record = BanRecord(
                user_id=user_id,
                banned_by='system',
                reason=ban_reason,
                warning_count=user_obj.warning_count,
                is_active=True
            )
            ban_repo.create(ban_record)
            
            # DM 발송
            try:
                admin_token = os.getenv('BOT_ACCESS_TOKEN')
                if admin_token:
                    mastodon = create_mastodon_client(admin_token)
                    dm_message = f"커뮤니티 규정에 따라 경고 3회 누적으로 계정이 비활성화되었습니다. 자세한 내용은 관리자에게 문의해주세요."
                    send_dm(mastodon, user_obj.username, dm_message)
            except Exception as e:
                # 로깅만 수행
                print(f"Error sending auto-ban DM to {user_obj.username}: {e}")

    def get_warning(self, warning_id: int) -> Optional[Warning]:
        """ID로 경고를 조회합니다."""
        # [수정됨] 올바른 Repository 호출
        return self.warning_repo.find_by_id(warning_id)

    def get_all_warnings(self) -> List[Dict]:
        """모든 경고를 조회합니다 (딕셔너리 리스트 반환)."""
        warnings = self.warning_repo.find_all()
        # API 응답을 위해 to_dict() 처리
        return [w.to_dict() for w in warnings]

    def get_user_warnings(self, user_id: str) -> List[Dict]:
        """특정 유저의 모든 경고를 조회합니다."""
        warnings = self.warning_repo.find_by_user(user_id)
        return [w.to_dict() for w in warnings]

    def get_warnings_by_type(self, warning_type: str) -> List[Warning]:
        return self.warning_repo.find_by_type(warning_type)

    def update_dm_sent(self, warning_id: int, dm_sent: bool) -> Optional[Warning]:
        self.warning_repo.update_dm_sent(warning_id, dm_sent)
        return self.warning_repo.find_by_id(warning_id)

    def get_user_warning_statistics(self, user_id: str) -> Dict[str, Any]:
        warnings = self.warning_repo.find_by_user(user_id)
        by_type: Dict[str, int] = {}
        for warning in warnings:
            warning_type = warning.warning_type
            by_type[warning_type] = by_type.get(warning_type, 0) + 1

        user = self.user_repo.find_by_id(user_id)
        warning_count = user.warning_count if user else 0

        return {
            'total_warnings': len(warnings),
            'warning_count': warning_count,
            'by_type': by_type
        }

    def is_user_at_risk_of_ban(self, user_id: str) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False
        return user.warning_count >= self.AT_RISK_THRESHOLD

    def get_warning_counts_by_type(self) -> Dict[str, int]:
        all_warnings = self.warning_repo.find_all()
        counts: Dict[str, int] = {}
        for warning in all_warnings:
            warning_type = warning.warning_type
            counts[warning_type] = counts.get(warning_type, 0) + 1
        return counts
