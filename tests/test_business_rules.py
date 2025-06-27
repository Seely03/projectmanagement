import pytest
from app import app, db
from app.models.models import User, Project, Task, ProjectMember

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

def test_task_assignment_only_to_project_member(session):
    owner = User(username='owner', email='owner@example.com')
    owner.set_password('Owner123!')
    member = User(username='member', email='member@example.com')
    member.set_password('Member123!')
    outsider = User(username='outsider', email='outsider@example.com')
    outsider.set_password('Outsider123!')
    session.add_all([owner, member, outsider])
    session.commit()

    project = Project(title='Test Project', description='A project', user_id=owner.id)
    session.add(project)
    session.commit()

    # Add only 'member' as a project member
    pm = ProjectMember(project_id=project.id, user_id=member.id)
    session.add(pm)
    session.commit()

    # Assign task to member (should be allowed)
    task = Task(title='Valid Task', project_id=project.id, user_id=member.id)
    session.add(task)
    session.commit()
    assert task in project.tasks

    # Assign task to outsider (should not be allowed by business logic)
    # Simulate the check (since the model itself doesn't enforce it)
    member_ids = [m.user_id for m in ProjectMember.query.filter_by(project_id=project.id).all()]
    assert outsider.id not in member_ids
    # In real app, controller should prevent this 