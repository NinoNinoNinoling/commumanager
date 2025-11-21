"""
BanRecord 모델

유저 아웃(ban) 기록을 나타내는 데이터 모델
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class BanRecord:
    """
    유저 아웃 기록 모델

    ban_records 테이블의 데이터를 나타냅니다.

    Attributes:
        id: 기록 ID (자동 생성)
        user_id: 아웃된 유저의 Mastodon ID
        banned_at: 아웃 시각
        banned_by: 아웃 처리자 (관리자 이름 또는 'system')
        reason: 아웃 사유
        warning_count: 아웃 당시 경고 횟수
        evidence_snapshot: 증거 스냅샷 (선택)
        is_active: 활성 상태 (True: 아웃 중, False: 해제됨)
        unbanned_at: 아웃 해제 시각 (선택)
        unbanned_by: 아웃 해제자 (선택)
        unban_reason: 아웃 해제 사유 (선택)
    """
    user_id: str
    banned_by: str
    reason: str
    warning_count: Optional[int] = None
    evidence_snapshot: Optional[str] = None
    is_active: bool = True
    id: Optional[int] = None
    banned_at: Optional[datetime] = None
    unbanned_at: Optional[datetime] = None
    unbanned_by: Optional[str] = None
    unban_reason: Optional[str] = None

    def to_dict(self) -> dict:
        """
        BanRecord를 딕셔너리로 변환합니다.

        Returns:
            BanRecord 데이터를 담은 딕셔너리
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'banned_at': self.banned_at.isoformat() if self.banned_at else None,
            'banned_by': self.banned_by,
            'reason': self.reason,
            'warning_count': self.warning_count,
            'evidence_snapshot': self.evidence_snapshot,
            'is_active': self.is_active,
            'unbanned_at': self.unbanned_at.isoformat() if self.unbanned_at else None,
            'unbanned_by': self.unbanned_by,
            'unban_reason': self.unban_reason
        }
