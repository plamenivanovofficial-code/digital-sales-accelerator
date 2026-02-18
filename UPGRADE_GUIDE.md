# OMEGA v4 TITANIUM - UPGRADE GUIDE

## 🎯 What Changed?

### 1. ✅ ENV-Based Reviewer Names
**Before:** Hardcoded names (Maria, Shadow) in code  
**After:** Configurable via `.env` file - use ANY names!

### 2. 🚀 Scalable Review System
**Before:** Limited to 2 reviewers with hardcoded columns  
**After:** New `asset_reviews` table supports unlimited reviewers

### 3. 📋 Scanner Activity Log
**Before:** No visibility into what scanner processed  
**After:** Full log of all scanned files with status tracking

### 4. 🔍 Live Scanner Status
**Before:** Basic progress bar  
**After:** Detailed real-time stats with processing log

---

## 📦 Quick Start

### Step 1: Configure Your Reviewers

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your names:
```env
REVIEW_USER_1_NAME=YourName
REVIEW_USER_1_PASSWORD=yourpass

REVIEW_USER_2_NAME=PartnerName
REVIEW_USER_2_PASSWORD=partnerpass

GEMINI_API_KEY=your_api_key_here
```

### Step 2: Migrate Existing Reviews (ONE TIME)

If you have existing reviews in the database, run this ONCE:

```bash
python migrate_reviews.py
```

This will copy all your old reviews (reviewed_by_shadow/maria) to the new system.

**Note:** Old columns remain for backward compatibility but are now deprecated.

### Step 3: Start Using!

```bash
python -m streamlit run app.py
```

---

## 🆕 New Features

### Scanner Log
- **Location:** Scanner tab → "Scanner Processing Log"
- **What it shows:**
  - ✅ Successfully added files
  - ⏭️ Skipped duplicates  
  - ❌ Errors with details
  - 📊 Real-time stats per scan session

### Review System
- **Automatic migration** from old system
- **Supports unlimited reviewers** (just add to config)
- **Clean separation** of review data
- **Full audit trail** of who reviewed what and when

---

## 🔧 Technical Details

### New Database Tables

#### `asset_reviews`
Stores individual reviews:
```sql
asset_id | reviewer_name | decision | note | reviewed_at
---------|---------------|----------|------|------------
1        | Shadow        | approved | Good | 2024-02-09
1        | Leksy         | approved | Nice | 2024-02-09
```

#### `scanner_log`
Tracks all processed files:
```sql
scan_session_id | file_name | action | status | scanned_at
----------------|-----------|--------|--------|------------
scan_1_123      | file.psd  | added  | success| 2024-02-09
```

### Migration Safety
- ✅ Safe to run multiple times
- ✅ Old columns kept for compatibility
- ✅ No data loss
- ✅ Gradual rollout possible

---

## 🎓 How Review System Works Now

### Previous System (Deprecated)
```python
# Hardcoded columns in assets table
reviewed_by_shadow = 1  # Boolean
reviewed_by_maria = 1   # Boolean
shadow_note = "..."
maria_note = "..."
```

### New System (Scalable)
```python
# One row per review in asset_reviews table
database.add_review(conn, asset_id, "Shadow", "approved", "Looks good!")
database.add_review(conn, asset_id, "Leksy", "approved", "Love it!")

# Get review state for any number of reviewers
required = ["Shadow", "Leksy", "Ivan"]  # Can be 2, 5, 10, etc.
status = database.get_asset_review_state(conn, asset_id, required)
# Returns: 'approved' | 'rejected' | 'pending'
```

---

## ❓ FAQ

### Q: Will my existing reviews be lost?
**A:** No! Run `migrate_reviews.py` to copy them to the new system.

### Q: Can I add more reviewers later?
**A:** Yes! Just add them to `.env` and the system automatically adapts.

### Q: What if migration fails?
**A:** It's safe to run multiple times. Old data is never deleted.

### Q: Do I need to change my workflow?
**A:** No! The UI works the same, just with your custom names.

---

## 🚨 Important Notes

1. **Run migration ONCE** after updating
2. **Set .env BEFORE first run** to use custom names
3. **Old columns still work** but are deprecated
4. **Scanner log is automatic** - no config needed

---

## 🎉 Benefits

✅ **Privacy:** No more fake names in your production system  
✅ **Scalability:** Add reviewers without code changes  
✅ **Transparency:** See exactly what scanner processed  
✅ **Audit Trail:** Full history of who reviewed what  
✅ **Performance:** Better database design  

---

## 🐛 Troubleshooting

### Scanner log shows no data
- Make sure you started a new scan AFTER the update
- Old scans won't have logs (logging is new feature)

### Reviews not showing
- Run `migrate_reviews.py` if you have old data
- Check `.env` has correct reviewer names
- Verify database has `asset_reviews` table

### Names still showing as "Maria"
- Restart the app after changing `.env`
- Clear browser cache if needed
- Check `.env` is in the correct directory

---

Ready to go! 🚀
