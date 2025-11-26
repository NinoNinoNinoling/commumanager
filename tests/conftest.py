"""
Pytest configuration and fixtures
"""
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
from admin_web.app import create_app

@pytest.fixture
def app(temp_db):
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE_PATH": temp_db,
    })
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def temp_db():
    """Create a temporary database for testing and yield its path."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db_connection(temp_db):
    """Create a database connection"""
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    
    yield conn
    
    conn.close()
