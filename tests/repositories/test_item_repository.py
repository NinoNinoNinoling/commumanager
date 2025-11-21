"""
ItemRepository tests

Following TDD principles
"""
import sqlite3
import pytest
from datetime import datetime


@pytest.fixture
def item_repo(temp_db):
    from init_db import initialize_database
    from admin_web.repositories.item_repository import ItemRepository
    initialize_database(temp_db)
    return ItemRepository(temp_db)


def test_should_create_item(item_repo):
    from admin_web.models.item import Item
    item = Item(name='배지', price=100, category='badge')
    created = item_repo.create(item)
    assert created.id is not None
    assert created.name == '배지'


def test_should_find_item_by_id(item_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", ('아이템', 100))
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    item = item_repo.find_by_id(item_id)
    assert item is not None
    assert item.id == item_id


def test_should_return_none_when_item_not_found(item_repo):
    item = item_repo.find_by_id(99999)
    assert item is None


def test_should_find_all_items(item_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    for i in range(3):
        cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", (f'아이템{i}', 100))
    conn.commit()
    conn.close()
    
    items = item_repo.find_all()
    assert len(items) == 3


def test_should_filter_by_category(item_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price, category) VALUES (?, ?, ?)", ('배지1', 100, 'badge'))
    cursor.execute("INSERT INTO items (name, price, category) VALUES (?, ?, ?)", ('배지2', 200, 'badge'))
    cursor.execute("INSERT INTO items (name, price, category) VALUES (?, ?, ?)", ('기타', 50, 'other'))
    conn.commit()
    conn.close()
    
    items = item_repo.find_by_category('badge')
    assert len(items) == 2


def test_should_filter_active_items_only(item_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price, is_active) VALUES (?, ?, ?)", ('활성', 100, 1))
    cursor.execute("INSERT INTO items (name, price, is_active) VALUES (?, ?, ?)", ('비활성', 100, 0))
    conn.commit()
    conn.close()
    
    items = item_repo.find_by_active(True)
    assert len(items) == 1
    assert items[0].name == '활성'


def test_should_update_item(item_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", ('원래', 100))
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    from admin_web.models.item import Item
    updated_item = Item(id=item_id, name='수정', price=200)
    result = item_repo.update(updated_item)
    assert result.name == '수정'
    assert result.price == 200


def test_should_deactivate_item(item_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price, is_active) VALUES (?, ?, ?)", ('아이템', 100, 1))
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    item_repo.deactivate(item_id)
    item = item_repo.find_by_id(item_id)
    assert item.is_active is False


def test_should_count_all_items(item_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    for i in range(5):
        cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", (f'아이템{i}', 100))
    conn.commit()
    conn.close()
    
    count = item_repo.count()
    assert count == 5
