"""
OMEGA v4 TITANIUM - DATABASE MODULE
Complete database schema for business intelligence
"""

import sqlite3
import json
from pathlib import Path
import pandas as pd
import config
import re


# ═══════════════════════════════════════════════════════════
# DATABASE INITIALIZATION
# ═══════════════════════════════════════════════════════════
def init_db(db_path="omega_titanium.db"):
    """Initialize database with all tables"""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # ───────────────────────────────────────────────────────
    # ASSETS
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            file_hash TEXT UNIQUE,

            category TEXT,
            rating INTEGER,
            ai_price TEXT,
            market_research TEXT,
            platform TEXT,
            keywords TEXT,
            summary TEXT,
            seo_pack TEXT,

            status TEXT DEFAULT 'pending',
            reviewed_by_shadow INTEGER DEFAULT 0,
            reviewed_by_maria INTEGER DEFAULT 0,
            shadow_note TEXT,
            maria_note TEXT,
            final_decision TEXT,

            collections TEXT,
            custom_tags TEXT,

            date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_reviewed DATETIME,
            date_listed DATETIME,
            date_sold DATETIME,

            file_size INTEGER,
            file_extension TEXT,

            UNIQUE(name, path)
        )
        """
        
    )

    # ───────────────────────────────────────────────────────
    # SALES
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            platform TEXT,
            sale_price REAL NOT NULL,
            sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            buyer_country TEXT,
            notes TEXT,
            FOREIGN KEY (asset_id) REFERENCES assets(id)
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # TASKS (KANBAN)
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'Medium',
            assigned_to TEXT,
            related_asset_id INTEGER,
            created_by TEXT,
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_completed DATETIME
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # COLLECTIONS
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            target_price REAL,
            status TEXT DEFAULT 'planning',
            asset_ids TEXT,
            created_by TEXT,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # ACTIVITY LOG
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            action TEXT,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # AI CHAT HISTORY
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            message TEXT,
            response TEXT,
            context TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # SECURITY
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            username TEXT,
            ip TEXT,
            user_agent TEXT,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS banned_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT,
            entity_value TEXT UNIQUE,
            reason TEXT,
            banned_by TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # ASSET REVIEWS (Scalable multi-reviewer system)
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS asset_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            reviewer_name TEXT NOT NULL,
            decision TEXT NOT NULL,
            note TEXT,
            reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets(id),
            UNIQUE(asset_id, reviewer_name)
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # SCANNER LOG (Track processed files)
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scanner_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_session_id TEXT NOT NULL,
            zone_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_hash TEXT,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # BUSINESS IDEAS
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS business_ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            sector TEXT,
            problem TEXT,
            solution TEXT,
            target_customer TEXT,
            differentiator TEXT,
            created_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS business_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER,
            evaluation_json TEXT,
            model_used TEXT,
            created_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ───────────────────────────────────────────────────────
    # SCAN JOBS (Background scanner)
    # ───────────────────────────────────────────────────────
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT,
            base_path TEXT,
            file_types_json TEXT,
            status TEXT DEFAULT 'queued',  -- queued|running|completed|stopped|error
            started_at DATETIME,
            finished_at DATETIME,
            total_candidates INTEGER DEFAULT 0,
            seen_files INTEGER DEFAULT 0,
            processed INTEGER DEFAULT 0,
            skipped INTEGER DEFAULT 0,
            errors INTEGER DEFAULT 0,
            current_file TEXT,
            last_error TEXT,
            stop_requested INTEGER DEFAULT 0,
            created_by TEXT
        )
        """
    )

    conn.commit()
    return conn


def strip_html(text):
    """Remove HTML tags from a string (safe for None)."""
    if text is None:
        return ""
    return re.sub(r"<[^>]+>", "", str(text)).strip()


# ═══════════════════════════════════════════════════════════
# ASSET REVIEWS (Scalable System)
# ═══════════════════════════════════════════════════════════
def add_review(conn, asset_id, reviewer_name, decision, note=None):
    """
    Add or update a review for an asset.
    
    Args:
        asset_id: Asset ID
        reviewer_name: Name of reviewer (from config.REVIEW_USER_1_NAME, etc.)
        decision: 'approved' or 'rejected'
        note: Optional review note
    """
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO asset_reviews (asset_id, reviewer_name, decision, note)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(asset_id, reviewer_name) 
        DO UPDATE SET decision=?, note=?, reviewed_at=CURRENT_TIMESTAMP
        """,
        (asset_id, reviewer_name, decision, note, decision, note),
    )
    conn.commit()


def get_asset_reviews(conn, asset_id):
    """
    Get all reviews for an asset.
    
    Returns:
        List of dicts with keys: reviewer_name, decision, note, reviewed_at
    """
    c = conn.cursor()
    rows = c.execute(
        """
        SELECT reviewer_name, decision, note, reviewed_at
        FROM asset_reviews
        WHERE asset_id = ?
        ORDER BY reviewed_at DESC
        """,
        (asset_id,),
    ).fetchall()
    
    return [dict(row) for row in rows]


def get_asset_review_state(conn, asset_id, required_reviewers):
    """
    Calculate aggregate review status for an asset.
    
    Args:
        asset_id: Asset ID
        required_reviewers: List of reviewer names that must approve
        
    Returns:
        'approved' if all required reviewers approved
        'rejected' if any reviewer rejected
        'pending' otherwise
    """
    reviews = get_asset_reviews(conn, asset_id)
    review_map = {r['reviewer_name']: r['decision'] for r in reviews}
    
    # If any rejection → rejected
    if 'rejected' in review_map.values():
        return 'rejected'
    
    # If all required approved → approved
    if all(review_map.get(name) == 'approved' for name in required_reviewers):
        return 'approved'
    
    # Otherwise → pending
    return 'pending'


def migrate_legacy_reviews(conn):
    """
    ONE-TIME migration: copy old reviewed_by_shadow/maria columns to asset_reviews table.
    Safe to run multiple times (uses ON CONFLICT).
    """
    c = conn.cursor()
    
    # Get all assets with legacy reviews
    assets = c.execute(
        """
        SELECT id, reviewed_by_shadow, reviewed_by_maria, shadow_note, maria_note
        FROM assets
        WHERE reviewed_by_shadow != 0 OR reviewed_by_maria != 0
        """
    ).fetchall()
    
    migrated = 0
    for row in assets:
        asset_id = row['id']
        
        # Migrate shadow/user1 review
        if row['reviewed_by_shadow'] != 0:
            decision = 'approved' if row['reviewed_by_shadow'] == 1 else 'rejected'
            add_review(conn, asset_id, config.REVIEW_USER_1_NAME, decision, row['shadow_note'])
            migrated += 1
        
        # Migrate maria/user2 review
        if row['reviewed_by_maria'] != 0:
            decision = 'approved' if row['reviewed_by_maria'] == 1 else 'rejected'
            add_review(conn, asset_id, config.REVIEW_USER_2_NAME, decision, row['maria_note'])
            migrated += 1
    
    conn.commit()
    return migrated


# ═══════════════════════════════════════════════════════════
# SCANNER LOG
# ═══════════════════════════════════════════════════════════
def log_scan_file(conn, session_id, zone_name, file_path, file_name, file_hash, action, status, error_msg=None):
    """
    Log a processed file during scanning.
    
    Args:
        session_id: Unique ID for this scan session
        zone_name: Name of zone being scanned
        file_path: Full file path
        file_name: File name only
        file_hash: File hash (if computed)
        action: 'added', 'skipped_duplicate', 'skipped_blacklist', 'error'
        status: 'success', 'skipped', 'error'
        error_msg: Error message if status='error'
    """
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO scanner_log 
        (scan_session_id, zone_name, file_path, file_name, file_hash, action, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (session_id, zone_name, str(file_path), file_name, file_hash, action, status, error_msg),
    )
    conn.commit()


def get_scan_logs(conn, session_id=None, limit=100):
    """
    Get scanner logs.
    
    Args:
        session_id: Optional filter by scan session
        limit: Max number of logs to return
        
    Returns:
        List of log dicts
    """
    c = conn.cursor()
    
    if session_id:
        rows = c.execute(
            """
            SELECT * FROM scanner_log
            WHERE scan_session_id = ?
            ORDER BY scanned_at DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
    else:
        rows = c.execute(
            """
            SELECT * FROM scanner_log
            ORDER BY scanned_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    
    return [dict(row) for row in rows]


def get_scan_summary(conn, session_id):
    """
    Get summary statistics for a scan session.
    
    Returns:
        Dict with counts: total, added, skipped, errors
    """
    c = conn.cursor()
    
    row = c.execute(
        """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN action = 'added' THEN 1 ELSE 0 END) as added,
            SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
        FROM scanner_log
        WHERE scan_session_id = ?
        """,
        (session_id,),
    ).fetchone()
    
    return dict(row) if row else {'total': 0, 'added': 0, 'skipped': 0, 'errors': 0}


# ═══════════════════════════════════════════════════════════
# ASSETS
# ═══════════════════════════════════════════════════════════
def save_asset(conn, file_path, analysis, file_hash, user="System"):
    c = conn.cursor()
    file_path = Path(file_path)
    size = file_path.stat().st_size if file_path.exists() else 0
def save_asset(conn, file_path, analysis, file_hash, user="System"):
    c = conn.cursor()
    file_path = Path(file_path)
    size = file_path.stat().st_size if file_path.exists() else 0

    # ✅ sanitize incoming fields (STOP HTML in DB)
    clean_name = strip_html(file_path.name)

    raw_summary = analysis.get("summary")
    clean_summary = strip_html(raw_summary) if raw_summary else ""

    raw_keywords = analysis.get("keywords")
    clean_keywords = strip_html(raw_keywords) if raw_keywords else ""

    raw_platform = analysis.get("platform")
    clean_platform = strip_html(raw_platform) if raw_platform else ""

    raw_category = analysis.get("category")
    clean_category = strip_html(raw_category) if raw_category else ""

    raw_price = analysis.get("price")
    clean_price = strip_html(raw_price) if raw_price else ""

    c.execute(
        """
        INSERT OR IGNORE INTO assets
        (name, path, file_hash, category, rating, ai_price, platform,
         keywords, summary, file_size, file_extension)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            clean_name,
            str(file_path),
            file_hash,
            clean_category,
            analysis.get("rating"),
            clean_price,
            clean_platform,
            clean_keywords,
            clean_summary,
            size,
            file_path.suffix,
        ),
    )

    conn.commit()
    log_activity(conn, user, "asset_added", "asset", c.lastrowid, clean_name)

    c.execute(
        """
        INSERT OR IGNORE INTO assets
        (name, path, file_hash, category, rating, ai_price, platform,
         keywords, summary, file_size, file_extension)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            file_path.name,
            str(file_path),
            file_hash,
            analysis.get("category"),
            analysis.get("rating"),
            analysis.get("price"),
            analysis.get("platform"),
            analysis.get("keywords"),
            analysis.get("summary"),
            size,
            file_path.suffix,
        ),
    )

    conn.commit()
    log_activity(conn, user, "asset_added", "asset", c.lastrowid, file_path.name)


def is_duplicate(conn, file_hash):
    c = conn.cursor()
    row = c.execute("SELECT id FROM assets WHERE file_hash=?", (file_hash,)).fetchone()
    return bool(row)


# ═══════════════════════════════════════════════════════════
# TASKS
# ═══════════════════════════════════════════════════════════
def add_task(conn, title, description, assigned_to, priority, created_by):
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO tasks (title, description, assigned_to, priority, created_by)
        VALUES (?,?,?,?,?)
        """,
        (title, description, assigned_to, priority, created_by),
    )
    conn.commit()


def update_task_status(conn, task_id, status, current_user):
    c = conn.cursor()

    # Update status only
    c.execute(
        "UPDATE tasks SET status=? WHERE id=?",
        (status, task_id),
    )

    # Log who did it (you already have activity_log 👍)
    log_activity(
        conn,
        current_user,
        "task_status_updated",
        "task",
        task_id,
        f"Status changed to {status}",
    )

    conn.commit()




# ═══════════════════════════════════════════════════════════
# ACTIVITY
# ═══════════════════════════════════════════════════════════
def log_activity(conn, user, action, target_type, target_id, details=""):
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO activity_log (user, action, target_type, target_id, details)
        VALUES (?,?,?,?,?)
        """,
        (user, action, target_type, target_id, details),
    )
    conn.commit()


def get_recent_activity(conn, limit=10):
    return pd.read_sql(
        "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?",
        conn,
        params=(limit,),
    )


# ═══════════════════════════════════════════════════════════
# FINANCIALS
# ═══════════════════════════════════════════════════════════
def get_financial_stats(conn):
    c = conn.cursor()

    inv = (
        c.execute(
            "SELECT SUM(CAST(REPLACE(ai_price,'$','') AS REAL)) FROM assets WHERE status!='sold'"
        ).fetchone()[0]
        or 0
    )

    sales = c.execute("SELECT SUM(sale_price) FROM sales").fetchone()[0] or 0

    from datetime import datetime

    current_month = datetime.now().strftime("%Y-%m")
    month_sales = (
        c.execute(
            "SELECT SUM(sale_price) FROM sales WHERE strftime('%Y-%m', sale_date) = ?",
            (current_month,),
        ).fetchone()[0]
        or 0
    )

    return {
        "inventory_value": inv,
        "total_sales": sales,
        "month_sales": month_sales,
        "ready_to_list": c.execute(
            "SELECT COUNT(*) FROM assets WHERE status='approved'"
        ).fetchone()[0],
    }


# ═══════════════════════════════════════════════════════════
# BUSINESS IDEAS
# ═══════════════════════════════════════════════════════════
def add_business_idea(conn, **data):
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO business_ideas
        (title, sector, problem, solution, target_customer, differentiator, created_by)
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            data["title"],
            data.get("sector"),
            data.get("problem"),
            data.get("solution"),
            data.get("target_customer"),
            data.get("differentiator"),
            data.get("created_by"),
        ),
    )
    conn.commit()
    return c.lastrowid


def list_business_ideas(conn):
    return pd.read_sql("SELECT * FROM business_ideas ORDER BY id DESC", conn)


# ═══════════════════════════════════════════════════════════
# SECURITY FUNCTIONS
# ═══════════════════════════════════════════════════════════
def get_security_events(conn, limit=100):
    """Get recent security events from audit log"""
    try:
        query = """
        SELECT event_type, username, ip_address, details, timestamp
        FROM audit_log
        ORDER BY id DESC
        LIMIT ?
        """
        return pd.read_sql(query, conn, params=(limit,))
    except Exception:
        return pd.DataFrame(
            columns=["event_type", "username", "ip_address", "details", "timestamp"]
        )


def get_banned_entities(conn):
    """Get list of banned IPs and usernames"""
    try:
        query = """
        SELECT ban_type, ban_value, reason, banned_by, banned_at, unbanned_at
        FROM banlist
        WHERE unbanned_at IS NULL
        ORDER BY banned_at DESC
        """
        return pd.read_sql(query, conn)
    except Exception:
        return pd.DataFrame(
            columns=[
                "ban_type",
                "ban_value",
                "reason",
                "banned_by",
                "banned_at",
                "unbanned_at",
            ]
        )


def add_sale(conn, asset_id, sale_price, platform, buyer_info="", sale_date=None):
    """Record a sale"""
    c = conn.cursor()
    if sale_date is None:
        from datetime import datetime

        sale_date = datetime.now().strftime("%Y-%m-%d")

    c.execute(
        """
        INSERT INTO sales (asset_id, sale_price, platform, buyer_info, sale_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (asset_id, sale_price, platform, buyer_info, sale_date),
    )

    c.execute("UPDATE assets SET status='sold' WHERE id=?", (asset_id,))
    conn.commit()
    return c.lastrowid


def update_asset_review(conn, asset_id, reviewer, approved, note=""):
    """
    Update asset review status (NEW SCALABLE SYSTEM)
    Also updates legacy columns for backward compatibility
    """
    # Add review to new system
    decision = 'approved' if approved else 'rejected'
    add_review(conn, asset_id, reviewer, decision, note)
    
    # Update legacy columns for backward compatibility
    c = conn.cursor()
    
    if reviewer.lower() in ["shadow", config.REVIEW_USER_1_NAME.lower()]:
        c.execute(
            """
            UPDATE assets
            SET reviewed_by_shadow=?, shadow_note=?
            WHERE id=?
            """,
            (1 if approved else -1, note, asset_id),
        )
    elif reviewer.lower() in ["maria", config.REVIEW_USER_2_NAME.lower()]:
        c.execute(
            """
            UPDATE assets
            SET reviewed_by_maria=?, maria_note=?
            WHERE id=?
            """,
            (1 if approved else -1, note, asset_id),
        )
    
    # Update asset status based on new review system
    required_reviewers = [config.REVIEW_USER_1_NAME, config.REVIEW_USER_2_NAME]
    new_status = get_asset_review_state(conn, asset_id, required_reviewers)
    
    c.execute("UPDATE assets SET status=? WHERE id=?", (new_status, asset_id))
    conn.commit()


def get_review_status_display(conn, asset_id):
    """
    Get formatted review status for UI display.
    
    Returns:
        Dict with keys for each reviewer and their status emoji
        Example: {'Shadow': '✅', 'Leksy': '⏳'}
    """
    reviews = get_asset_reviews(conn, asset_id)
    review_map = {r['reviewer_name']: r['decision'] for r in reviews}
    
    required_reviewers = [config.REVIEW_USER_1_NAME, config.REVIEW_USER_2_NAME]
    
    result = {}
    for reviewer in required_reviewers:
        decision = review_map.get(reviewer)
        if decision == 'approved':
            result[reviewer] = '✅'
        elif decision == 'rejected':
            result[reviewer] = '❌'
        else:
            result[reviewer] = '⏳'
    
    return result


def create_collection(conn, name, description, created_by):
    """Create a new collection"""
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO collections (name, description, created_by)
        VALUES (?, ?, ?)
        """,
        (name, description, created_by),
    )
    conn.commit()
    return c.lastrowid


def save_ai_chat(conn, user_message, ai_response, username):
    """Save AI chat to database"""
    c = conn.cursor()
    try:
        c.execute(
            """
            INSERT INTO ai_chats (username, user_message, ai_response, timestamp)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (username, user_message, ai_response),
        )
        conn.commit()
    except Exception:
        pass


def save_business_evaluation(conn, idea_id, evaluation, model_used, created_by):
    """Save business idea evaluation"""
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO business_evaluations (idea_id, evaluation, model_used, created_by)
        VALUES (?, ?, ?, ?)
        """,
        (idea_id, json.dumps(evaluation), model_used, created_by),
    )
    conn.commit()
    return c.lastrowid


def get_latest_business_evaluation(conn, idea_id):
    """Get latest evaluation for a business idea"""
    c = conn.cursor()
    try:
        row = c.execute(
            """
            SELECT evaluation, model_used, created_by, created_at
            FROM business_evaluations
            WHERE idea_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (idea_id,),
        ).fetchone()

        if row:
            return {
                "evaluation": json.loads(row[0]),
                "model_used": row[1],
                "created_by": row[2],
                "created_at": row[3],
            }
        return None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# BACKGROUND SCANNER (SCAN JOBS)
# ═══════════════════════════════════════════════════════════
def create_scan_job(conn, zone, base_path, file_types, created_by):
    """Create a scan job and return its id."""
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO scan_jobs (zone, base_path, file_types_json, status, created_by)
        VALUES (?, ?, ?, 'queued', ?)
        """,
        (
            zone,
            str(base_path),
            json.dumps(sorted(list(file_types)) if file_types else None),
            created_by,
        ),
    )
    conn.commit()
    return c.lastrowid


def set_scan_job_status(conn, job_id, status, last_error=None):
    c = conn.cursor()
    if status == "running":
        c.execute(
            """
            UPDATE scan_jobs
            SET status=?, started_at=CURRENT_TIMESTAMP, last_error=?
            WHERE id=?
            """,
            (status, last_error, job_id),
        )
    elif status in ("completed", "stopped", "error"):
        c.execute(
            """
            UPDATE scan_jobs
            SET status=?, finished_at=CURRENT_TIMESTAMP, last_error=?
            WHERE id=?
            """,
            (status, last_error, job_id),
        )
    else:
        c.execute(
            "UPDATE scan_jobs SET status=?, last_error=? WHERE id=?",
            (status, last_error, job_id),
        )
    conn.commit()


def update_scan_job_progress(conn, job_id, **kwargs):
    """Update numeric counters / current file. Only updates provided fields."""
    allowed = {
        "total_candidates",
        "seen_files",
        "processed",
        "skipped",
        "errors",
        "current_file",
        "last_error",
    }
    parts = []
    vals = []
    for k, v in kwargs.items():
        if k in allowed:
            parts.append(f"{k}=?")
            vals.append(v)
    if not parts:
        return
    vals.append(job_id)
    sql = "UPDATE scan_jobs SET " + ", ".join(parts) + " WHERE id=?"
    c = conn.cursor()
    c.execute(sql, tuple(vals))
    conn.commit()


def request_stop_scan_job(conn, job_id):
    c = conn.cursor()
    c.execute("UPDATE scan_jobs SET stop_requested=1 WHERE id=?", (job_id,))
    conn.commit()


def get_scan_job(conn, job_id):
    c = conn.cursor()
    row = c.execute("SELECT * FROM scan_jobs WHERE id=?", (job_id,)).fetchone()
    return dict(row) if row else None


def list_scan_jobs(conn, limit=20):
    return pd.read_sql(
        "SELECT * FROM scan_jobs ORDER BY id DESC LIMIT ?",
        conn,
        params=(limit,),
    )
