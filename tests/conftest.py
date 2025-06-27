import os
import pytest
from app import app

@pytest.fixture(scope='session', autouse=True)
def ensure_test_db():
    # Abort if not using the dedicated test DB
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri != 'sqlite:///test.db':
        raise RuntimeError(f"Tests must use the dedicated test database! Current URI: {db_uri}")
    yield

@pytest.fixture(scope='session', autouse=True)
def cleanup_test_db():
    yield
    if os.path.exists('test.db'):
        os.remove('test.db') 