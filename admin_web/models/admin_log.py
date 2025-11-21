"""AdminLog 모델"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AdminLog:
    admin_name: str
    action_type: str
    id: Optional[int] = None
    target_user: Optional[str] = None
    details: Optional[str] = None
    timestamp: Optional[datetime] = None
