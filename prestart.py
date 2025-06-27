from app import app, db
from alembic.config import Config
from alembic import command
import os
from sqlalchemy import inspect

def run_migrations():
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), 'migrations', 'alembic.ini'))
    command.upgrade(alembic_cfg, 'head')

def seed_sample_data():
    # Check if the 'user' table exists before seeding
    inspector = inspect(db.engine)
    if 'user' in inspector.get_table_names():
        from app.models.models import User
        if db.session.query(User).count() == 0:
            import sample_data  # This will run the seeding logic

with app.app_context():
    run_migrations()
    # Dispose and re-create the session to ensure new tables are visible
    db.session.remove()
    db.engine.dispose()
    seed_sample_data() 