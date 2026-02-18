"""
OMEGA v4 TITANIUM - SECURITY MODULE
Authentication, audit logging, login alerts, banlist (LAN-focused)
"""
import streamlit as st
import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import config

# Legacy session tracking file (kept for backward compatibility)
SESSION_LOG = "system_log.json"


def hash_password(password: str) -> str:
    """SHA-256 password hashing (not used for auth yet; kept for future)."""
    return hashlib.sha256(password.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────
# Client metadata (best-effort; depends on Streamlit runtime)
# ─────────────────────────────────────────────────────────────
def get_client_headers() -> dict:
    """
    Return request headers if available (best-effort).
    Uses Streamlit public API: st.context.headers
    """
    try:
        h = st.context.headers  # Streamlit-supported API
        return dict(h) if h else {}
    except Exception:
        return {}


def get_client_ip() -> str:
    """
    Best-effort client IP.
    Note: In pure Streamlit this is often 'unknown' unless behind a proxy
    that sets X-Forwarded-For / X-Real-IP.
    """
    headers = get_client_headers()

    # Header keys can vary in casing; normalize
    headers_norm = {str(k).lower(): v for k, v in headers.items()}

    xff = headers_norm.get("x-forwarded-for") or headers_norm.get("x-real-ip")
    if xff:
        return str(xff).split(",")[0].strip()

    return "unknown"


def get_user_agent() -> str:
    headers = get_client_headers()
    headers_norm = {str(k).lower(): v for k, v in headers.items()}
    return str(headers_norm.get("user-agent", "unknown"))


# ─────────────────────────────────────────────────────────────
# DB helpers (use main app DB path; do not depend on app init order)
# ─────────────────────────────────────────────────────────────
def _open_db() -> sqlite3.Connection:
    return sqlite3.connect(config.DATABASE_PATH, check_same_thread=False)


def ensure_security_tables(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS security_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        username TEXT,
        ip TEXT,
        user_agent TEXT,
        details TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS banned_entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_value TEXT NOT NULL,
        reason TEXT,
        banned_by TEXT,
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(entity_type, entity_value)
    )''')
    conn.commit()


def log_event(event_type: str, username: str = None, details: str = "", ip: str = None, user_agent: str = None) -> None:
    """Write an audit event to DB + legacy JSON file (best-effort)."""
    ip = ip or get_client_ip()
    user_agent = user_agent or get_user_agent()

    # DB log
    try:
        conn = _open_db()
        ensure_security_tables(conn)
        conn.execute(
            "INSERT INTO security_events (event_type, username, ip, user_agent, details) VALUES (?,?,?,?,?)",
            (event_type, username, ip, user_agent, details),
        )
        conn.commit()
        conn.close()
    except Exception:
        # Never crash app due to logging
        pass

    # Legacy JSON log (keep)
    try:
        if Path(SESSION_LOG).exists():
            with open(SESSION_LOG, 'r', encoding='utf-8') as f:
                log = json.load(f)
        else:
            log = []
        log.append({
            "timestamp": datetime.now().isoformat(),
            "user": username,
            "action": event_type,
            "details": details,
            "ip": ip,
        })
        with open(SESSION_LOG, 'w', encoding='utf-8') as f:
            json.dump(log[-1000:], f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def is_banned(username: str = None, ip: str = None) -> tuple[bool, str]:
    """Check if username or ip is currently banned."""
    ip = ip or get_client_ip()
    try:
        conn = _open_db()
        ensure_security_tables(conn)
        cur = conn.cursor()
        # Username ban
        if username:
            cur.execute(
                "SELECT reason FROM banned_entities WHERE entity_type='username' AND entity_value=? AND is_active=1",
                (username,),
            )
            row = cur.fetchone()
            if row:
                conn.close()
                return True, f"Banned user: {row[0] or 'no reason'}"
        # IP ban
        if ip and ip != "unknown":
            cur.execute(
                "SELECT reason FROM banned_entities WHERE entity_type='ip' AND entity_value=? AND is_active=1",
                (ip,),
            )
            row = cur.fetchone()
            if row:
                conn.close()
                return True, f"Banned IP: {row[0] or 'no reason'}"
        conn.close()
        return False, ""
    except Exception:
        return False, ""


def ban_entity(entity_type: str, entity_value: str, reason: str, banned_by: str) -> None:
    try:
        conn = _open_db()
        ensure_security_tables(conn)
        conn.execute(
            "INSERT OR REPLACE INTO banned_entities (entity_type, entity_value, reason, banned_by, is_active) VALUES (?,?,?,?,1)",
            (entity_type, entity_value, reason, banned_by),
        )
        conn.commit()
        conn.close()
        log_event("ban", username=banned_by, details=f"{entity_type}:{entity_value} | {reason}")
    except Exception:
        pass


def unban_entity(entity_type: str, entity_value: str, unbanned_by: str) -> None:
    try:
        conn = _open_db()
        ensure_security_tables(conn)
        conn.execute(
            "UPDATE banned_entities SET is_active=0 WHERE entity_type=? AND entity_value=?",
            (entity_type, entity_value),
        )
        conn.commit()
        conn.close()
        log_event("unban", username=unbanned_by, details=f"{entity_type}:{entity_value}")
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────────────────────
def check_password() -> bool:
    """Dual-user authentication system (backward compatible)."""

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.session_state.display_name = None

    if st.session_state.authenticated:
        return True

    # Best-effort ban check before showing login UI
    ip = get_client_ip()
    banned, reason = is_banned(ip=ip)
    if banned:
        st.error(f"⛔ Access denied ({reason}).")
        st.stop()

    # Login screen
    st.markdown(
        """
        <div style='text-align: center; padding: 50px;'>
            <h1>🛡️ OMEGA v4 TITANIUM</h1>
            <h3>Business Intelligence System</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🔐 Login")

        username = st.selectbox("👤 User", list(config.USERS.keys()))
        password = st.text_input("🔑 Password", type="password")

        # Ban check can be username-specific too
        banned_u, reason_u = is_banned(username=username, ip=ip)
        if banned_u:
            st.error(f"⛔ Access denied ({reason_u}).")
            st.stop()

        if st.button("LOGIN", use_container_width=True):
            user_config = config.USERS.get(username)

            if user_config and password == user_config["password"]:
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.user_role = user_config.get("role", "viewer")
                st.session_state.display_name = user_config.get("display_name", username)

                log_event("login_success", username=username, ip=ip)
                st.success(f"✅ Welcome, {st.session_state.display_name}!")
                st.rerun()
            else:
                log_event("login_failed", username=username, ip=ip)
                st.error("❌ Invalid credentials!")

    st.stop()
    return False



def get_current_user() -> str:
    return st.session_state.get("current_user")

def is_admin_user() -> bool:
    return (st.session_state.get("user_role") == "admin")

def logout() -> None:
    user = st.session_state.get("current_user")
    log_event("logout", username=user)
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_role = None
    st.session_state.display_name = None
    st.rerun()


# ─────────────────────────────────────────────────────────────
# Notifications (admin)
# ─────────────────────────────────────────────────────────────
def notify_new_logins(conn: sqlite3.Connection, current_user: str, is_admin: bool) -> None:
    """Show toast/banner when a new login is detected."""
    if not is_admin:
        return

    ensure_security_tables(conn)

    # Track last seen event id per session
    if "last_security_event_id" not in st.session_state:
        st.session_state.last_security_event_id = 0

    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, ip, created_at FROM security_events WHERE event_type='login_success' AND id > ? ORDER BY id ASC",
        (st.session_state.last_security_event_id,),
    )
    rows = cur.fetchall()
    if not rows:
        return

    for event_id, username, ip, created_at in rows:
        # Don't notify on your own login
        if username and username != current_user:
            msg = f"⚠️ New login: {username} ({ip})"
            try:
                st.toast(msg)  # Streamlit >= 1.25
            except Exception:
                st.info(msg)
        st.session_state.last_security_event_id = max(st.session_state.last_security_event_id, event_id)


# ─────────────────────────────────────────────────────────────
# Existing helper functions (kept)
# ─────────────────────────────────────────────────────────────
def monitor_activity(user, action, details=""):
    """Backwards compatible alias."""
    log_event(action, username=user, details=details)


def is_safe_path(path, base_dir):
    """Prevent path traversal attacks."""
    try:
        path_resolved = Path(path).resolve()
        base_resolved = Path(base_dir).resolve()
        return base_resolved in path_resolved.parents or path_resolved == base_resolved
    except Exception:
        return False


def validate_scan_path(path):
    """Validate if path is safe to scan."""
    path = Path(path)
    path_str = str(path).upper()

    for blocked in config.BLOCKED_DRIVES:
        if path_str.startswith(blocked):
            return False, f"⛔ Access denied: System drive {blocked} is blocked"

    for blacklisted in config.BLACKLIST_PATHS:
        if blacklisted in path_str:
            return False, f"⛔ Access denied: Path contains blacklisted folder '{blacklisted}'"

    if not path.exists():
        return False, f"⚠️ Path does not exist: {path}"

    return True, ""


def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ""
    dangerous = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    sanitized = text
    for d in dangerous:
        sanitized = sanitized.replace(d, "")
    return sanitized
