from app import app
from app import db
from app.models.models import User, Project, Task
import os
from flask_migrate import upgrade

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
    print("Running migrations...")
    try:
        with app.app_context():
            # Use Flask-Migrate instead of raw Alembic
            upgrade()
            print("Migrations completed successfully")
    except Exception as e:
        print(f"Migration failed: {e}")
        print("Creating tables directly as fallback...")
        with app.app_context():
            db.create_all()
            print("Tables created successfully")

def seed_sample_data():
    print("Checking if database needs seeding...")
    try:
        with app.app_context():
            from app.models.models import User
            
            # Check if there are any users
            if User.query.count() == 0:
                print("No users found, seeding database...")
                
                # Import and run the enhanced seeding function
                try:
                    from sample_data import seed_database
                    seed_database()
                except Exception as e:
                    print(f"Error running enhanced seed_database: {e}")
                    print("Trying fallback seeding method...")
                    # Fallback to importing the module (if it runs on import)
                    import sample_data
                    
            else:
                print(f"Database already has {User.query.count()} users, skipping seeding")
                
    except Exception as e:
        print(f"Error during seeding: {e}")
        print("Creating basic admin user as fallback...")
        create_basic_admin()

def create_basic_admin():
    """Fallback function to create a basic admin user"""
    try:
        with app.app_context():
            from app.models.models import User
            from app import db
            
            # Check if admin already exists
            if User.query.filter_by(email='admin@admin.com').first():
                print("Admin user already exists")
                return
                
            admin_user = User(
                username='admin',
                email='admin@admin.com',
                is_admin=True
            )
            admin_user.set_password('Admin123!')
            
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Created basic admin user: admin@admin.com / Admin123!")
            
    except Exception as e:
        print(f"Error creating basic admin: {e}")

# If running under Gunicorn (i.e., not __main__), run migrations and seed
if os.environ.get('RENDER', None) or os.environ.get('GUNICORN_CMD_ARGS', None) or os.environ.get('DYNO', None):
    run_migrations()
    seed_sample_data()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))