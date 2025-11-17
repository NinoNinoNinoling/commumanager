"""
User Service
유저 관련 비즈니스 로직을 담당
"""
from typing import Optional, List, Dict, Any
from admin_web.repositories.user_repository import UserRepository


class UserService:
    """유저 비즈니스 로직 서비스"""

    def __init__(self, db_path: str):
        """
        Args:
            db_path: 데이터베이스 경로
        """
        self.user_repository = UserRepository(db_path)

    def get_or_create_user(self, mastodon_id: str, username: str,
                          display_name: str, is_admin: bool = False) -> Dict[str, Any]:
        """
        유저 조회 또는 생성 (OAuth 로그인용)

        Args:
            mastodon_id: 마스토돈 유저 ID
            username: 유저명
            display_name: 표시 이름
            is_admin: 관리자 여부

        Returns:
            유저 정보
        """
        # 기존 유저 조회
        user = self.user_repository.get_user_by_mastodon_id(mastodon_id)

        if user:
            return user

        # 신규 유저 생성
        user_id = self.user_repository.create_user(mastodon_id, username, display_name, is_admin)
        return self.user_repository.get_user_by_id(user_id)

    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        유저 정보 조회

        Args:
            user_id: 유저 ID

        Returns:
            유저 정보 또는 None
        """
        return self.user_repository.get_user_by_id(user_id)

    def adjust_user_currency(self, user_id: int, amount: int, reason: str = "") -> bool:
        """
        유저 재화 조정 (비즈니스 로직 포함)

        Args:
            user_id: 유저 ID
            amount: 변경할 재화량 (양수: 증가, 음수: 감소)
            reason: 변경 사유

        Returns:
            성공 여부
        """
        # 재화 감소시 잔액 확인
        if amount < 0:
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                return False

            current_currency = user.get('currency', 0)
            if current_currency + amount < 0:
                # 잔액 부족
                return False

        # 재화 업데이트
        success = self.user_repository.update_user_currency(user_id, amount)

        # TODO: 트랜잭션 로그 기록
        # if success and reason:
        #     transaction_dao.create_transaction(user_id, amount, reason)

        return success

    def get_users_paginated(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        페이지네이션된 유저 목록 조회

        Args:
            page: 페이지 번호 (1부터 시작)
            per_page: 페이지당 결과 수

        Returns:
            {
                'users': [...],
                'total': int,
                'page': int,
                'per_page': int,
                'total_pages': int
            }
        """
        offset = (page - 1) * per_page
        users = self.user_repository.get_all_users(limit=per_page, offset=offset)
        total = self.user_repository.get_user_count()
        total_pages = (total + per_page - 1) // per_page

        return {
            'users': users,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

    def is_admin(self, user_id: int) -> bool:
        """
        관리자 권한 확인

        Args:
            user_id: 유저 ID

        Returns:
            관리자 여부
        """
        user = self.user_repository.get_user_by_id(user_id)
        return user.get('is_admin', False) if user else False

    def get_user_statistics(self) -> Dict[str, Any]:
        """
        유저 통계 조회 (대시보드용)

        Returns:
            통계 정보
        """
        total_users = self.user_repository.get_user_count()

        # TODO: 추가 통계 정보
        # - 활성 유저 수
        # - 신규 유저 수 (최근 7일)
        # - 평균 재화량 등

        return {
            'total_users': total_users,
            # 'active_users': active_count,
            # 'new_users': new_count,
        }
