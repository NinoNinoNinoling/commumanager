from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AdminLog:
    """관리자 활동 로그 모델"""
    id: int
    admin_id: str
    action_type: str  # create, update, delete, warning, etc.
    target_type: str  # user, item, setting, etc.
    target_id: Optional[str]
    details: str      # JSON or Text description
    ip_address: Optional[str]
    created_at: datetime
