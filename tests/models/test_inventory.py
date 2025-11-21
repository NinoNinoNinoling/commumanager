"""Inventory model tests"""
from datetime import datetime
from dataclasses import asdict


def test_should_create_inventory_with_required_fields():
    from admin_web.models.inventory import Inventory
    inventory = Inventory(user_id='user@example.com', item_id=1, quantity=5)
    assert inventory.user_id == 'user@example.com'
    assert inventory.item_id == 1
    assert inventory.quantity == 5


def test_should_set_default_values():
    from admin_web.models.inventory import Inventory
    inventory = Inventory(user_id='user@example.com', item_id=1)
    assert inventory.id is None
    assert inventory.quantity == 1
    assert inventory.acquired_at is None


def test_should_serialize_to_dict():
    from admin_web.models.inventory import Inventory
    inventory = Inventory(id=1, user_id='user@example.com', item_id=1, quantity=5)
    inventory_dict = asdict(inventory)
    assert inventory_dict['id'] == 1
    assert inventory_dict['user_id'] == 'user@example.com'


def test_should_create_from_dict():
    from admin_web.models.inventory import Inventory
    data = {'id': 1, 'user_id': 'user@example.com', 'item_id': 1, 'quantity': 5}
    inventory = Inventory.from_dict(data)
    assert inventory.id == 1
    assert inventory.quantity == 5
