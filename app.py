from app import app
from app import db
from app.models.models import User, Project, Task
import os
from alembic.config import Config
from alembic import command
from flask_migrate import upgrade

# Add CSP headers to allow scripts to run
@app.after_request
def add_csp_headers(response):
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://cdn.jsdelivr.net https://code.jquery.com https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' "
        "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    # Try multiple header names to override any defaults
    response.headers['Content-Security-Policy'] = csp_policy
    response.headers['X-Content-Security-Policy'] = csp_policy
    # Remove any conflicting headers
    if 'X-Content-Type-Options' in response.headers:
        del response.headers['X-Content-Type-Options']
    return response

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
    try:
        # Run Flask-Migrate migrations
        upgrade()
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Migration failed: {e}")
        print("Creating tables directly...")
        db.create_all()
        print("Tables created successfully")

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