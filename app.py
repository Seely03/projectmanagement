from app import app
from app import db
from app.models.models import User, Project, Task
import os
from alembic.config import Config
from alembic import command

# Determine which auth method to use
use_cognito = os.environ.get('USE_COGNITO_AUTH', 'false').lower() == 'true'

if use_cognito:
    # Initialize Cognito authentication
    try:
        from app.config.cognito import CognitoConfig
        app.config.from_object(CognitoConfig)
        from app.controllers.auth_controller import setup_cognito_auth
        setup_cognito_auth()
        print("Using Cognito authentication")
    except Exception as e:
        print(f"Error setting up Cognito auth: {e}")
        print("Falling back to local authentication")
        from app.controllers.auth_controller import *
else:
    # Use local authentication (development)
    from app.controllers.auth_controller import *
    print("Using local authentication")

def run_migrations():
    # Path to alembic.ini
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), 'migrations', 'alembic.ini'))
    command.upgrade(alembic_cfg, 'head')

def seed_sample_data():
    from sample_data import app as sample_app
    # Only seed if there are no users
    with sample_app.app_context():
        from app.models.models import User
        from app import db
        if User.query.count() == 0:
            import sample_data  # This will run the seeding logic

# If running under Gunicorn (i.e., not __main__), run migrations and seed
if os.environ.get('RENDER', None) or os.environ.get('GUNICORN_CMD_ARGS', None) or os.environ.get('DYNO', None):
    with app.app_context():
        run_migrations()
        seed_sample_data()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 