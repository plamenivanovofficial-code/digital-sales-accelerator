"""
Database Update Script for OMEGA + AI Router Integration
Adds ai_provider column to assets table
"""

import sqlite3
import os

DB_PATH = 'omega_titanium.db'

def update_database():
    """Add ai_provider column if it doesn't exist"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print(f"   Make sure you're running this from your OMEGA directory")
        return False
    
    print(f"🔧 Updating database: {DB_PATH}")
    
    # Backup first
    backup_path = 'omega_titanium_backup.db'
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Created backup: {backup_path}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(assets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'ai_provider' in columns:
            print("✅ ai_provider column already exists")
        else:
            # Add column
            cursor.execute("""
                ALTER TABLE assets 
                ADD COLUMN ai_provider TEXT DEFAULT 'gemini'
            """)
            print("✅ Added ai_provider column")
        
        # Commit changes
        conn.commit()
        print("✅ Database updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA + AI Router - Database Update")
    print("=" * 60)
    print()
    
    success = update_database()
    
    print()
    if success:
        print("🎉 Database update complete!")
        print()
        print("Next steps:")
        print("1. Run: python test_integration.py")
        print("2. Then: streamlit run app.py")
    else:
        print("⚠️  Database update failed")
        print("Please check the error message above")
