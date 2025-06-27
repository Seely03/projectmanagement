import pytest
from app import app, db
from app.models.models import User

@pytest.fixture(scope='module')
def test_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()


def test_password_hashing(session):
    user = User(username='testuser', email='test@example.com')
    user.set_password('MySecret123!')
    session.add(user)
    session.commit()

    assert user.password_hash != 'MySecret123!'
    assert user.check_password('MySecret123!')
    assert not user.check_password('WrongPassword') 