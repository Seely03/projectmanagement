import pytest
from app import app, db
from app.models.models import User, Project, Task

@pytest.fixture(scope='function')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for full isolation
    app.config['WTF_CSRF_ENABLED'] = False  # Optional: disable CSRF for easier form testing

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def register(client, username, email, password, confirm=None):
    if confirm is None:
        confirm = password
    response = client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': confirm
    }, follow_redirects=True)
    assert b'Login' in response.data or b'Successfully registered' in response.data
    return response

def login(client, username, password):
    response = client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)
    assert b'Logout' in response.data or b'Dashboard' in response.data
    return response

def logout(client):
    return client.get('/logout', follow_redirects=True)

from app.models.models import User, Project, Task

def test_project_crud(test_client):
    client = test_client
    register(client, 'projuser', 'projuser@example.com', 'ProjUser123!')
    login(client, 'projuser', 'ProjUser123!')

    # Create project
    rv = client.post('/projects/new', data={'title': 'Test Project', 'description': 'A test'}, follow_redirects=True)
    assert b'Test Project' in rv.data

    # Edit project
    with client.application.app_context():
        project = Project.query.filter_by(title='Test Project').first()
        assert project is not None
        rv = client.post(f'/projects/{project.id}/edit', data={'title': 'Edited Project', 'description': 'Updated'}, follow_redirects=True)
        assert b'Edited Project' in rv.data

    # Delete project
    rv = client.post(f'/projects/{project.id}/delete', follow_redirects=True)
    assert b'Projects' in rv.data or b'projects' in rv.data


def test_task_crud(test_client):
    client = test_client
    register(client, 'taskuser', 'taskuser@example.com', 'TaskUser123!')
    login(client, 'taskuser', 'TaskUser123!')

    # Create project
    rv = client.post('/projects/new', data={'title': 'Task Project', 'description': 'For tasks'}, follow_redirects=True)
    assert b'Task Project' in rv.data

    with client.application.app_context():
        project = Project.query.filter_by(title='Task Project').first()
        user = User.query.filter_by(username='taskuser').first()
        assert project is not None and user is not None
        project_id = project.id
        user_id = user.id

    # Create task
    rv = client.post(f'/projects/{project_id}/tasks/new', data={
        'title': 'Test Task',
        'description': 'A task',
        'status': 'To Do',   
        'priority': 'Medium',
        'user_id': user_id,
        'effort_points': 1,
    }, follow_redirects=True)


    # Edit task
    with client.application.app_context():
        task = Task.query.filter_by(title='Test Task').first()
        assert task is not None
        task_id = task.id

    rv = client.post(f'/projects/{project_id}/tasks/{task_id}/edit', data={
        'title': 'Test Task Edited',
        'description': 'Updated',
        'status': 'Done',
        'priority': 'High',
        'user_id': user_id
    }, follow_redirects=True)
    assert b'Test Task Edited' in rv.data

    # Delete task
    rv = client.post(f'/projects/{project_id}/tasks/{task_id}/delete', follow_redirects=True)
    assert b'Tasks' in rv.data or b'tasks' in rv.data
