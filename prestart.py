from app import app
from alembic.config import Config
from alembic import command
import os

def run_migrations():
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), 'migrations', 'alembic.ini'))
    command.upgrade(alembic_cfg, 'head')

def seed_sample_data():
    from sample_data import app as sample_app
    with sample_app.app_context():
        from app.models.models import User
        from app import db
        if User.query.count() == 0:
            import sample_data

with app.app_context():
    run_migrations()
    seed_sample_data() 