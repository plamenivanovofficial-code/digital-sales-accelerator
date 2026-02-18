"""
OMEGA v4 TITANIUM - LEGACY REVIEW MIGRATION
Run this ONCE to migrate old reviewed_by_shadow/maria data to new asset_reviews table
"""

import config
import database

def main():
    print("🔄 Starting legacy review migration...")
    print(f"📂 Database: {config.DATABASE_PATH}")
    
    # Connect to database
    conn = database.init_db(config.DATABASE_PATH)
    
    # Run migration
    migrated_count = database.migrate_legacy_reviews(conn)
    
    print(f"✅ Migration complete!")
    print(f"📊 Migrated {migrated_count} reviews")
    print(f"👥 Reviewers: {config.REVIEW_USER_1_NAME}, {config.REVIEW_USER_2_NAME}")
    
    # Show some stats
    c = conn.cursor()
    total_reviews = c.execute("SELECT COUNT(*) FROM asset_reviews").fetchone()[0]
    print(f"📈 Total reviews in new table: {total_reviews}")
    
    conn.close()
    print("\n💡 You can now safely use the new review system!")
    print("⚠️  Old columns (reviewed_by_shadow/maria) still exist but are deprecated")

if __name__ == "__main__":
    main()
