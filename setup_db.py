from app import app, db
from app.models.models import User, Project, Task, ProjectMember

def setup_database():
    print("Setting up database from scratch...")
    
    # Create a new application context
    with app.app_context():
        # Drop all tables if they exist
        db.drop_all()
        print("✓ Dropped all existing tables")
        
        print("\nDatabase reset complete! Now run:")
        print("flask db upgrade")

if __name__ == "__main__":
    setup_database() 