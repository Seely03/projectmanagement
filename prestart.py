from app import app, db
from alembic.config import Config
from alembic import command
import os
from sqlalchemy import inspect

def run_migrations():
    print("Running migrations...")
    alembic_ini_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'alembic.ini'))
    alembic_cfg = Config(alembic_ini_path)
    command.upgrade(alembic_cfg, 'head')
    print("Migrations complete.")

def seed_sample_data():
    print("Checking for 'user' table before seeding...")
    inspector = inspect(db.engine)
    if 'user' in inspector.get_table_names():
        from app.models.models import User
        if db.session.query(User).count() == 0:
            print("Seeding sample data...")
            import sample_data
            print("Seeding complete.")
        else:
            print("Users already seeded.")
    else:
        print("'user' table does not exist. Skipping seeding.")

with app.app_context():
    run_migrations()
    db.session.remove()
    db.engine.dispose()
    seed_sample_data()
