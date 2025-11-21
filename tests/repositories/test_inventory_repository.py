"""InventoryRepository tests"""
import sqlite3
import pytest


@pytest.fixture
def inventory_repo(temp_db):
    from init_db import initialize_database
    from admin_web.repositories.inventory_repository import InventoryRepository
    initialize_database(temp_db)
    
    # Create test user and item
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (mastodon_id, username, role) VALUES (?, ?, ?)", ('user@example.com', 'user', 'user'))
    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", ('아이템', 100))
    conn.commit()
    conn.close()
    
    return InventoryRepository(temp_db)


def test_should_add_item_to_inventory(inventory_repo):
    from admin_web.models.inventory import Inventory
    inventory = Inventory(user_id='user@example.com', item_id=1, quantity=5)
    created = inventory_repo.add_or_update(inventory)
    assert created.id is not None
    assert created.quantity == 5


def test_should_increase_quantity_if_exists(inventory_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)", ('user@example.com', 1, 3))
    conn.commit()
    conn.close()
    
    from admin_web.models.inventory import Inventory
    inventory = Inventory(user_id='user@example.com', item_id=1, quantity=2)
    updated = inventory_repo.add_or_update(inventory)
    assert updated.quantity == 5


def test_should_find_user_inventory(inventory_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", ('아이템2', 200))
    cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)", ('user@example.com', 1, 3))
    cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)", ('user@example.com', 2, 2))
    conn.commit()
    conn.close()
    
    inventories = inventory_repo.find_by_user('user@example.com')
    assert len(inventories) == 2


def test_should_check_if_user_owns_item(inventory_repo, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)", ('user@example.com', 1, 1))
    conn.commit()
    conn.close()
    
    assert inventory_repo.user_owns_item('user@example.com', 1) is True
    assert inventory_repo.user_owns_item('user@example.com', 999) is False
