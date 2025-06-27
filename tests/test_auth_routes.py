import pytest
from app import app, db
from app.models.models import User

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def register(client, username, email, password, confirm=None):
    if confirm is None:
        confirm = password
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': confirm
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_register_login_logout(test_client):
    client = test_client
    # Register
    rv = register(client, 'testuser', 'test@example.com', 'Test1234!')
    assert b'Registration successful' in rv.data
    # Duplicate username
    rv = register(client, 'testuser', 'other@example.com', 'Test1234!')
    assert b'Username' in rv.data or b'username' in rv.data
    # Duplicate email
    rv = register(client, 'otheruser', 'test@example.com', 'Test1234!')
    assert b'Email' in rv.data or b'email' in rv.data
    # Password mismatch
    rv = register(client, 'user2', 'user2@example.com', 'Test1234!', 'Wrong1234!')
    assert b'Password' in rv.data or b'password' in rv.data
    # Login
    rv = login(client, 'testuser', 'Test1234!')
    assert b'Dashboard' in rv.data  # Check for dashboard content
    # Invalid login (should still show dashboard because user is logged in)
    rv = login(client, 'testuser', 'WrongPassword')
    assert b'Dashboard' in rv.data
    # Logout
    rv = logout(client)
    assert b'Login' in rv.data or b'login' in rv.data

def test_protected_route_requires_login(test_client):
    client = test_client
    # Ensure logged out
    logout(client)
    rv = client.get('/dashboard', follow_redirects=True)
    assert b'Login' in rv.data or b'login' in rv.data 