import pytest
from app import app, db
from app.models.models import User, Project, Task

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

def test_project_task_relationship(session):
    user = User(username='owner', email='owner@example.com')
    user.set_password('Owner123!')
    session.add(user)
    session.commit()

    project = Project(title='Test Project', description='A project', user_id=user.id)
    session.add(project)
    session.commit()

    task1 = Task(title='Task 1', project_id=project.id, user_id=user.id)
    task2 = Task(title='Task 2', project_id=project.id, user_id=user.id)
    session.add_all([task1, task2])
    session.commit()

    assert len(project.tasks) == 2
    assert task1 in project.tasks
    assert task2 in project.tasks
    assert task1.project == project
    assert task2.project == project 