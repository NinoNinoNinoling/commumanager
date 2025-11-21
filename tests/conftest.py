"""
Pytest configuration and fixtures
"""
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db_connection(temp_db):
    """Create a database connection"""
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    
    yield conn
    
    conn.close()
