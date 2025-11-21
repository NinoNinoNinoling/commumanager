"""ItemService tests"""
import sqlite3
import pytest


@pytest.fixture
def item_service(temp_db):
    from init_db import initialize_database
    from admin_web.services.item_service import ItemService
    initialize_database(temp_db)
    return ItemService(temp_db)


def test_should_create_item(item_service):
    from admin_web.models.item import Item
    item = Item(name='배지', price=100, category='badge')
    created = item_service.create_item(item)
    assert created['item'].id is not None


def test_should_validate_price_positive(item_service):
    from admin_web.models.item import Item
    import pytest
    item = Item(name='배지', price=-100)
    with pytest.raises(ValueError, match='Price must be positive'):
        item_service.create_item(item)


def test_should_get_all_active_items(item_service, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price, is_active) VALUES (?, ?, ?)", ('활성', 100, 1))
    cursor.execute("INSERT INTO items (name, price, is_active) VALUES (?, ?, ?)", ('비활성', 100, 0))
    conn.commit()
    conn.close()
    
    items = item_service.get_active_items()
    assert len(items) == 1
