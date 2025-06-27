from app import app, db
from alembic.config import Config
from alembic import command
import os

def run_migrations():
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), 'migrations', 'alembic.ini'))
    command.upgrade(alembic_cfg, 'head')

def seed_sample_data():
    from app.models.models import User
    # Only seed if there are no users
    if User.query.count() == 0:
        import sample_data  # This will run the seeding logic

with app.app_context():
    run_migrations()
    # Dispose and re-create the session to ensure new tables are visible
    db.session.remove()
    db.engine.dispose()
    seed_sample_data() 