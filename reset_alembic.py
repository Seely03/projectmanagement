import os
import shutil
from pathlib import Path

def reset_database():
    print("Starting fresh database setup...")
    
    # 1. Remove migrations directory
    migrations_dir = Path("migrations")
    if migrations_dir.exists():
        print("Removing migrations directory...")
        shutil.rmtree(migrations_dir)
        print("✓ Migrations directory removed")
    
    # 2. Remove database file
    db_file = Path("project_manager.db")
    if db_file.exists():
        print("Removing database file...")
        db_file.unlink()
        print("✓ Database file removed")
    
    print("\nClean slate achieved! Now run these commands in order:")
    print("1. flask db init")
    print("2. flask db migrate -m 'Initial migration'")
    print("3. flask db upgrade")

if __name__ == "__main__":
    reset_database()