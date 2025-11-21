"""ShopService tests"""
import sqlite3
import pytest


@pytest.fixture
def shop_service(temp_db):
    from init_db import initialize_database
    from admin_web.services.shop_service import ShopService
    initialize_database(temp_db)
    
    # Create test user and item
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (mastodon_id, username, role, balance) VALUES (?, ?, ?, ?)", 
                  ('user@example.com', 'user', 'user', 1000))
    cursor.execute("INSERT INTO items (name, price, is_active, current_stock) VALUES (?, ?, ?, ?)", 
                  ('배지', 100, 1, 10))
    conn.commit()
    conn.close()
    
    return ShopService(temp_db)


def test_should_purchase_item(shop_service, temp_db):
    result = shop_service.purchase_item('user@example.com', 1, 2)
    assert result['success'] is True
    assert result['new_balance'] == 800


def test_should_rollback_on_insufficient_balance(shop_service, temp_db):
    result = shop_service.purchase_item('user@example.com', 1, 20)
    assert result['success'] is False
    assert 'Insufficient balance' in result['error']


def test_should_rollback_on_inactive_item(shop_service, temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET is_active = 0 WHERE id = 1")
    conn.commit()
    conn.close()
    
    result = shop_service.purchase_item('user@example.com', 1, 1)
    assert result['success'] is False
    assert 'not available' in result['error']
