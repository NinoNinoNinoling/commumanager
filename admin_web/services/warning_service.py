"""WarningService

Warning 관련 비즈니스 로직을 처리하는 서비스 계층
"""
from typing import List, Optional, Dict, Any

from admin_web.models.warning import Warning
from admin_web.repositories.warning_repository import WarningRepository
from admin_web.repositories.user_repository import UserRepository


class WarningService:
    """
    Warning 비즈니스 로직을 처리하는 Service
    """

    # 유효한 경고 유형 정의
    VALID_WARNING_TYPES = ['activity', 'isolation', 'bias', 'avoidance']

    # 자동 아웃 위험 기준 (경고 횟수)
    AT_RISK_THRESHOLD = 2

    def __init__(self, db_path: str = 'economy.db'):
        """
        WarningService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.warning_repo = WarningRepository(db_path)
        self.user_repo = UserRepository(db_path)


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

        Args:
            user_id: 유저의 Mastodon ID
            warning_type: 경고 유형 (activity, isolation, bias, avoidance)
            message: 경고 메시지
            admin_name: 경고를 발행한 관리자 이름
            check_period_hours: 활동량 체크 기간 (시간)
            required_replies: 필요한 답글 수
            actual_replies: 실제 답글 수

        Returns:
            경고와 업데이트된 유저 정보를 담은 딕셔너리

        Raises:
            ValueError: 유효하지 않은 경고 유형인 경우
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

        # Warning 생성 및 User warning_count 증가
        created_warning = self.warning_repo.create(warning)
        self.user_repo.increment_warning_count(user_id)
        updated_user = self.user_repo.find_by_id(user_id)

        # 3회 도달 시 자동 아웃 로직 (이후 구현 예정)

        return {
            'warning': created_warning,
            'user': updated_user
        }

    def get_warning(self, warning_id: int) -> Optional[Warning]:
        """
        ID로 경고를 조회합니다.

        Args:
            warning_id: 경고 ID

        Returns:
            찾은 경우 Warning 객체, 아니면 None
        """
        return self.warning_repo.find_by_id(warning_id)

    def get_user_warnings(self, user_id: str) -> List[Warning]:
        """
        특정 유저의 모든 경고를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            경고 리스트 (최신순)
        """
        return self.warning_repo.find_by_user(user_id)

    def get_warnings_by_type(self, warning_type: str) -> List[Warning]:
        """
        유형별로 경고를 조회합니다.

        Args:
            warning_type: 경고 유형

        Returns:
            해당 유형의 경고 리스트
        """
        return self.warning_repo.find_by_type(warning_type)

    def update_dm_sent(self, warning_id: int, dm_sent: bool) -> Optional[Warning]:
        """
        경고의 DM 전송 상태를 업데이트합니다.

        Args:
            warning_id: 경고 ID
            dm_sent: DM 전송 여부

        Returns:
            업데이트된 Warning 객체
        """
        self.warning_repo.update_dm_sent(warning_id, dm_sent)
        return self.warning_repo.find_by_id(warning_id)

    def get_user_warning_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        유저의 경고 통계를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            경고 통계 딕셔너리 (total_warnings, warning_count, by_type)
        """

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
        """
        유저가 자동 아웃 위험 상태인지 확인합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            경고 횟수가 기준치 이상이면 True
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False
        return user.warning_count >= self.AT_RISK_THRESHOLD

    def get_warning_counts_by_type(self) -> Dict[str, int]:
        """
        전체 시스템의 유형별 경고 수를 계산합니다.

        Returns:
            경고 유형별 카운트 딕셔너리
        """
        all_warnings = self.warning_repo.find_all()

        counts: Dict[str, int] = {}
        for warning in all_warnings:
            warning_type = warning.warning_type
            counts[warning_type] = counts.get(warning_type, 0) + 1

        return counts
