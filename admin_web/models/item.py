"""
Item 모델

상점에서 판매되는 아이템 정보를 나타냅니다.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Item:
    """
    상점 아이템을 위한 Item 모델

    Attributes:
        id: Primary key (선택, 데이터베이스에서 설정)
        name: 아이템 이름 (필수)
        description: 아이템 설명 (선택)
        price: 가격 (필수)
        category: 카테고리 (선택)
        image_url: 이미지 URL (선택)
        is_active: 활성 여부 (기본값: True)
        initial_stock: 초기 재고 (기본값: 0)
        current_stock: 현재 재고 (기본값: 0)
        sold_count: 판매 수량 (기본값: 0)
        is_unlimited_stock: 무제한 재고 여부 (기본값: False)
        max_purchase_per_user: 유저당 최대 구매 수량 (선택)
        total_sales: 총 판매액 (기본값: 0)
        created_at: 생성 시각 (선택, 데이터베이스에서 설정)
    """
    name: str
    price: int
    id: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    initial_stock: int = 0
    current_stock: int = 0
    sold_count: int = 0
    is_unlimited_stock: bool = False
    max_purchase_per_user: Optional[int] = None
    total_sales: int = 0
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Item을 JSON 직렬화를 위한 딕셔너리로 변환합니다.

        Returns:
            Item의 딕셔너리 표현
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'initial_stock': self.initial_stock,
            'current_stock': self.current_stock,
            'sold_count': self.sold_count,
            'is_unlimited_stock': self.is_unlimited_stock,
            'max_purchase_per_user': self.max_purchase_per_user,
            'total_sales': self.total_sales,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """
        딕셔너리로부터 Item을 생성합니다.

        Args:
            data: 아이템 데이터를 담은 딕셔너리

        Returns:
            Item 인스턴스
        """
        # Parse created_at
        created_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            else:
                created_at = data['created_at']

        return cls(
            id=data.get('id'),
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            category=data.get('category'),
            image_url=data.get('image_url'),
            is_active=data.get('is_active', True),
            initial_stock=data.get('initial_stock', 0),
            current_stock=data.get('current_stock', 0),
            sold_count=data.get('sold_count', 0),
            is_unlimited_stock=data.get('is_unlimited_stock', False),
            max_purchase_per_user=data.get('max_purchase_per_user'),
            total_sales=data.get('total_sales', 0),
            created_at=created_at
        )

    def is_active_item(self) -> bool:
        """
        아이템이 활성 상태인지 확인합니다.

        Returns:
            is_active가 True이면 True, 아니면 False
        """
        return self.is_active

    def has_stock(self) -> bool:
        """
        재고가 있는지 확인합니다.

        무제한 재고인 경우 항상 True를 반환합니다.

        Returns:
            재고가 있거나 무제한 재고이면 True, 아니면 False
        """
        if self.is_unlimited_stock:
            return True
        return self.current_stock > 0

    def is_purchasable(self) -> bool:
        """
        구매 가능한지 확인합니다.

        활성 상태이고 재고가 있어야 구매 가능합니다.

        Returns:
            활성 상태이고 재고가 있으면 True, 아니면 False
        """
        return self.is_active and self.has_stock()
