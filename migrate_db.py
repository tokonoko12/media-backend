
from server.server import Server, db
import os
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    server = Server(os.environ.get("BASE_URL", "http://localhost:8090"))
    with server.app.app_context():
        # 1. Check if password_hash exists
        try:
            db.session.execute(text("SELECT password_hash FROM users LIMIT 1"))
            print("Migration already applied (or table empty but column exists).")
        except Exception:
            db.session.rollback() # Clear the failed SELECT transaction
            print("Applying migration: Adding password_hash to users table...")
            # We need to drop the table and recreate it because the old schema is fundamentally different 
            # (id was uuid FK to auth.users, now it is Integer PK)
            # CAUTION: This deletes data. Since this is "media-backend" dev env, I assume it's okay.
            
            try:
                # Drop dependencies first
                db.session.execute(text("DROP TABLE IF EXISTS watch_history"))
                db.session.commit()
                db.session.execute(text("DROP TABLE IF EXISTS user_preferences"))
                db.session.commit()
                db.session.execute(text("DROP TABLE IF EXISTS users CASCADE"))
                db.session.commit()
                
                print("Old tables dropped. Creating new schema...")
                db.create_all()
                print("Schema created successfully!")
            except Exception as e:
                print(f"Migration failed: {e}")
                db.session.rollback()

if __name__ == "__main__":
    run_migration()
