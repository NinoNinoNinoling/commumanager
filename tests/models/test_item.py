"""
Item model tests

Following TDD principles:
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor if needed
"""
from datetime import datetime
from dataclasses import asdict
import json


def test_should_create_item_with_required_fields():
    """
    필수 필드로 Item을 생성할 수 있어야 한다

    RED: Item 모델이 아직 없으므로 실패할 것
    """
    from admin_web.models.item import Item

    # When: 필수 필드로 Item 생성
    item = Item(
        name='청동 배지',
        price=100
    )

    # Then: 필드 값이 올바르게 설정되어야 함
    assert item.name == '청동 배지'
    assert item.price == 100
    assert item.id is None
    assert item.is_active is True


def test_should_create_item_with_optional_fields():
    """
    선택 필드를 포함하여 Item을 생성할 수 있어야 한다
    """
    from admin_web.models.item import Item

    # When: 선택 필드 포함
    now = datetime.now()
    item = Item(
        id=1,
        name='금 배지',
        description='명예의 상징',
        price=500,
        category='badge',
        image_url='https://example.com/gold.png',
        is_active=True,
        initial_stock=100,
        current_stock=80,
        sold_count=20,
        is_unlimited_stock=False,
        max_purchase_per_user=1,
        total_sales=10000,
        created_at=now
    )

    # Then
    assert item.id == 1
    assert item.description == '명예의 상징'
    assert item.category == 'badge'
    assert item.image_url == 'https://example.com/gold.png'
    assert item.initial_stock == 100
    assert item.current_stock == 80
    assert item.sold_count == 20
    assert item.is_unlimited_stock is False
    assert item.max_purchase_per_user == 1
    assert item.total_sales == 10000
    assert item.created_at == now


def test_should_set_default_values():
    """
    기본값이 올바르게 설정되어야 한다
    """
    from admin_web.models.item import Item

    # When: 최소 필드로 생성
    item = Item(
        name='아이템',
        price=100
    )

    # Then: 기본값 확인
    assert item.id is None
    assert item.description is None
    assert item.category is None
    assert item.image_url is None
    assert item.is_active is True
    assert item.initial_stock == 0
    assert item.current_stock == 0
    assert item.sold_count == 0
    assert item.is_unlimited_stock is False
    assert item.max_purchase_per_user is None
    assert item.total_sales == 0
    assert item.created_at is None


def test_should_serialize_to_dict():
    """
    Item을 딕셔너리로 직렬화할 수 있어야 한다
    """
    from admin_web.models.item import Item

    # Given
    item = Item(
        id=1,
        name='배지',
        price=100,
        category='badge'
    )

    # When: 딕셔너리로 변환
    item_dict = asdict(item)

    # Then
    assert item_dict['id'] == 1
    assert item_dict['name'] == '배지'
    assert item_dict['price'] == 100
    assert item_dict['category'] == 'badge'


def test_should_serialize_to_json():
    """
    Item을 JSON으로 직렬화할 수 있어야 한다
    """
    from admin_web.models.item import Item

    # Given
    item = Item(
        name='배지',
        price=100
    )

    # When: to_dict() 메서드 호출
    item_dict = item.to_dict()

    # Then: JSON 직렬화 가능해야 함
    json_str = json.dumps(item_dict, ensure_ascii=False)
    assert '배지' in json_str
    assert '100' in json_str


def test_should_create_item_from_dict():
    """
    딕셔너리로부터 Item을 생성할 수 있어야 한다
    """
    from admin_web.models.item import Item

    # Given
    data = {
        'id': 1,
        'name': '배지',
        'price': 100,
        'category': 'badge',
        'is_active': True
    }

    # When: from_dict() 메서드 호출
    item = Item.from_dict(data)

    # Then
    assert item.id == 1
    assert item.name == '배지'
    assert item.price == 100
    assert item.category == 'badge'
    assert item.is_active is True


def test_should_validate_required_fields():
    """
    필수 필드 누락 시 오류가 발생해야 한다
    """
    from admin_web.models.item import Item
    import pytest

    # When/Then: name 누락
    with pytest.raises(TypeError):
        Item(price=100)

    # When/Then: price 누락
    with pytest.raises(TypeError):
        Item(name='아이템')


def test_should_check_if_active():
    """
    활성 상태를 확인할 수 있어야 한다
    """
    from admin_web.models.item import Item

    # Given: 활성 아이템
    item1 = Item(name='아이템1', price=100, is_active=True)

    # Given: 비활성 아이템
    item2 = Item(name='아이템2', price=100, is_active=False)

    # Then
    assert item1.is_active_item() is True
    assert item2.is_active_item() is False


def test_should_check_stock_availability():
    """
    재고 유무를 확인할 수 있어야 한다
    """
    from admin_web.models.item import Item

    # Given: 재고 있음
    item1 = Item(name='아이템1', price=100, current_stock=10)

    # Given: 재고 없음
    item2 = Item(name='아이템2', price=100, current_stock=0)

    # Given: 무제한 재고
    item3 = Item(name='아이템3', price=100, is_unlimited_stock=True)

    # Then
    assert item1.has_stock() is True
    assert item2.has_stock() is False
    assert item3.has_stock() is True  # 무제한은 항상 True


def test_should_check_purchasability():
    """
    구매 가능 여부를 확인할 수 있어야 한다 (활성 + 재고)
    """
    from admin_web.models.item import Item

    # Given: 활성 + 재고 있음
    item1 = Item(name='아이템1', price=100, is_active=True, current_stock=10)

    # Given: 활성 + 재고 없음
    item2 = Item(name='아이템2', price=100, is_active=True, current_stock=0)

    # Given: 비활성 + 재고 있음
    item3 = Item(name='아이템3', price=100, is_active=False, current_stock=10)

    # Then
    assert item1.is_purchasable() is True
    assert item2.is_purchasable() is False
    assert item3.is_purchasable() is False
