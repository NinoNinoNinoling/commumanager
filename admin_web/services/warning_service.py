"""
WarningService

Warning 관련 비즈니스 로직을 처리하는 서비스 계층
"""
import sqlite3
from typing import List, Optional, Dict, Any

from admin_web.models.warning import Warning
from admin_web.repositories.warning_repository import WarningRepository
from admin_web.repositories.user_repository import UserRepository


class WarningService:
    """
    Warning 비즈니스 로직을 처리하는 Service

    WarningRepository와 UserRepository를 조합하여
    경고 발행, 조회, 통계 등의 비즈니스 로직을 처리합니다.
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

        Warning 생성과 User의 warning_count 증가는 원자적으로 처리됩니다.
        경고 유형은 반드시 유효한 값이어야 합니다.

        Args:
            user_id: 유저의 Mastodon ID
            warning_type: 경고 유형 (activity, isolation, bias, avoidance)
            message: 경고 메시지
            admin_name: 경고를 발행하는 관리자 이름
            check_period_hours: 체크 기간 (시간 단위)
            required_replies: 필요한 답글 수
            actual_replies: 실제 답글 수

        Returns:
            생성된 경고와 업데이트된 유저 정보를 담은 딕셔너리

        Raises:
            ValueError: 유효하지 않은 경고 유형인 경우
        """
        # 경고 유형 검증
        if warning_type not in self.VALID_WARNING_TYPES:
            raise ValueError(f'Invalid warning type: {warning_type}')

        # Warning 생성
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

        # DB 연결 (트랜잭션 처리)
        conn = sqlite3.connect(self.db_path)
        try:
            # Warning 생성
            created_warning = self.warning_repo.create(warning)

            # User의 warning_count 증가
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET warning_count = warning_count + 1
                WHERE mastodon_id = ?
            """, (user_id,))
            conn.commit()

            # 업데이트된 유저 조회
            updated_user = self.user_repo.find_by_id(user_id)

            return {
                'warning': created_warning,
                'user': updated_user
            }
        finally:
            conn.close()

    def get_warning(self, warning_id: int) -> Optional[Warning]:
        """
        ID로 경고를 조회합니다.

        Args:
            warning_id: 경고 ID

        Returns:
            찾은 경우 Warning, 아니면 None
        """
        return self.warning_repo.find_by_id(warning_id)

    def get_user_warnings(self, user_id: str) -> List[Warning]:
        """
        특정 유저의 모든 경고를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저의 경고 리스트 (시간 역순)
        """
        return self.warning_repo.find_by_user(user_id)

    def get_warnings_by_type(self, warning_type: str) -> List[Warning]:
        """
        유형별로 경고를 조회합니다.

        Args:
            warning_type: 경고 유형

        Returns:
            지정된 유형의 경고 리스트 (시간 역순)
        """
        return self.warning_repo.find_by_type(warning_type)

    def update_dm_sent(self, warning_id: int, dm_sent: bool) -> Optional[Warning]:
        """
        경고의 DM 전송 상태를 업데이트합니다.

        Args:
            warning_id: 경고 ID
            dm_sent: DM 전송 성공 여부

        Returns:
            업데이트된 Warning, 찾지 못한 경우 None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE warnings
            SET dm_sent = ?
            WHERE id = ?
        """, (1 if dm_sent else 0, warning_id))

        conn.commit()
        conn.close()

        return self.warning_repo.find_by_id(warning_id)

    def get_user_warning_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        유저의 경고 통계를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            통계 정보 딕셔너리:
            - total_warnings: 총 경고 수 (Warning 테이블)
            - warning_count: 유저의 warning_count (User 테이블)
            - by_type: 유형별 경고 수 (Dict[str, int])
        """
        # 유저의 모든 경고 조회
        warnings = self.warning_repo.find_by_user(user_id)

        # 유형별 카운트 계산
        by_type: Dict[str, int] = {}
        for warning in warnings:
            warning_type = warning.warning_type
            by_type[warning_type] = by_type.get(warning_type, 0) + 1

        # 유저 정보에서 warning_count 조회
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

        warning_count가 2 이상이면 위험 상태로 판단합니다.
        (3회 도달 시 자동 아웃)

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            위험 상태이면 True, 아니면 False
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False

        return user.warning_count >= self.AT_RISK_THRESHOLD

    def get_warning_counts_by_type(self) -> Dict[str, int]:
        """
        전체 시스템의 유형별 경고 수를 계산합니다.

        Returns:
            유형별 경고 수 딕셔너리 (Dict[warning_type, count])
        """
        all_warnings = self.warning_repo.find_all()

        counts: Dict[str, int] = {}
        for warning in all_warnings:
            warning_type = warning.warning_type
            counts[warning_type] = counts.get(warning_type, 0) + 1

        return counts
