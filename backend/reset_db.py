import os
import sqlite3

def reset_test_database():
    """Reset the test database by removing it and recreating"""
    db_path = 'meeting_assistant.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Import and initialize the database
    from app import init_db
    init_db()
    print("Test database reset successfully")

if __name__ == '__main__':
    reset_test_database()

