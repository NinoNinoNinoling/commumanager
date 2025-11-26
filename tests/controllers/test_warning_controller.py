"""
WarningController tests
"""
import json
import pytest

@pytest.fixture
def temp_db_with_user(temp_db):
    """Fixture to create a temporary database with a user."""
    from init_db import initialize_database
    import sqlite3
    initialize_database(temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (mastodon_id, username, role) VALUES (?, ?, ?)", 
                   ('12345', 'testuser', 'user'))
    conn.commit()
    conn.close()
    return temp_db

def test_should_create_warning_manually(client, temp_db_with_user):
    """
    POST /api/v1/warnings
    Should create a warning manually and return 201 Created.
    """
    # Given
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin'

    warning_data = {
        "user_id": "12345",
        "warning_type": "activity",
        "message": "Manual warning for testing",
        "admin_name": "test_admin"
    }

    # When
    response = client.post('/api/v1/warnings',
                           data=json.dumps(warning_data),
                           content_type='application/json')

    # Then
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['warning']['user_id'] == '12345'
    assert data['warning']['warning_type'] == 'activity'
    assert data['warning']['message'] == "Manual warning for testing"
    assert data['user']['warning_count'] == 1

    # Verify in DB
    import sqlite3
    conn = sqlite3.connect(temp_db_with_user)
    cursor = conn.cursor()
    cursor.execute("SELECT warning_count FROM users WHERE mastodon_id = '12345'")
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM warnings WHERE user_id = '12345'")
    assert cursor.fetchone()[0] == 1
    conn.close()