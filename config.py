"""
OMEGA v4 TITANIUM - CONFIGURATION
All system settings in one place
"""
from pathlib import Path
import os
import json
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════
# SECURITY & AUTHENTICATION
# ═══════════════════════════════════════════════════════════
# Two-reviewer workflow (DB columns remain named shadow/leksy)
REVIEW_USER_1_NAME = os.getenv("REVIEW_USER_1_NAME", os.getenv("SHADOW_USERNAME", "Shadow"))
REVIEW_USER_2_NAME = os.getenv("REVIEW_USER_2_NAME", os.getenv("MARIA_USERNAME", "Maria"))

REVIEW_USER_1_PASSWORD = os.getenv("REVIEW_USER_1_PASSWORD", os.getenv("SHADOW_PASSWORD", "shadow123"))
REVIEW_USER_2_PASSWORD = os.getenv("REVIEW_USER_2_PASSWORD", os.getenv("MARIA_PASSWORD", "maria123"))

# Optional: define additional users as JSON in .env
# Example:
# USERS_JSON={"Ivan":{"password":"pass","role":"admin","display_name":"Ivan"},"Guest":{"password":"guest","role":"viewer","display_name":"Guest"}}
_USERS_JSON_RAW = os.getenv("USERS_JSON", "").strip()

USERS: dict = {}
if _USERS_JSON_RAW:
    try:
        parsed = json.loads(_USERS_JSON_RAW)
        if isinstance(parsed, dict):
            USERS = parsed
        else:
            USERS = {}
    except Exception:
        USERS = {}

# Always ensure the two reviewer users exist (used throughout the app)
USERS.setdefault(
    REVIEW_USER_1_NAME,
    {"password": REVIEW_USER_1_PASSWORD, "role": "admin", "display_name": REVIEW_USER_1_NAME},
)
USERS.setdefault(
    REVIEW_USER_2_NAME,
    {"password": REVIEW_USER_2_PASSWORD, "role": "admin", "display_name": REVIEW_USER_2_NAME},
)

# Legacy DB column mapping (reviewed_by_shadow/maria, shadow_note/maria_note)
DB_REVIEW_COL_USER_1 = "shadow"
DB_REVIEW_COL_USER_2 = "maria"

# ═══════════════════════════════════════════════════════════
# ALLOWED SCANNING ZONES (Multi-Drive Support)
# ═══════════════════════════════════════════════════════════
ALLOWED_ZONES = {
    "Локални Активи (D:)": Path(r"D:/buissnes-program/MyAssets"),
    "Външен Диск (F:)": Path(r"F:/"),
    "Проекти (D:)": Path(r"D:/Projects"),
    "External Drive 1": Path(r"E:/"),
    "External Drive 2": Path(r"G:/"),
}

# Blacklist paths (никога не се сканират)
BLACKLIST_PATHS = [
    "_LICHNO",
    "WINDOWS",
    "PROGRAM FILES",
    "PROGRAM FILES (X86)",
    "SYSTEM32",
    "$RECYCLE.BIN",
    "RECYCLER",
    "System Volume Information",
    "ProgramData",
    "AppData",
]

# Block system drives
BLOCKED_DRIVES = ["C:"]

# ═══════════════════════════════════════════════════════════
# AI CONFIGURATION
# ═══════════════════════════════════════════════════════════
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gemini-2.0-flash")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-1.5-flash")
AI_TIMEOUT = 20  # seconds


# Model selection preference order (will be intersected with listModels at runtime)
AI_MODEL_PREFERENCE = [
    os.getenv("PRIMARY_MODEL", "gemini-2.5-flash"),
    os.getenv("FALLBACK_MODEL", "gemini-2.0-flash"),
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
]

# ═══════════════════════════════════════════════════════════
# FILE TYPES & SECURITY
# ═══════════════════════════════════════════════════════════
ALLOWED_EXTENSIONS = {
    # Images
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg",
    # Design
    ".psd", ".ai", ".eps", ".sketch", ".fig", ".xd", ".indd",
    # Documents
    ".pdf", ".doc", ".docx", ".txt", ".md",
    # Archives
    ".zip", ".rar", ".7z",
    # Video/Audio
    ".mp4", ".mov", ".avi", ".mp3", ".wav", ".flac",
    # Code
    ".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".py", ".php",
    # 3D
    ".obj", ".fbx", ".blend", ".max", ".c4d", ".3ds",
}

BLOCKED_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".scr", ".vbs",
    ".jar", ".sh", ".app", ".deb", ".rpm", ".msi",
    ".dll", ".so", ".sys",
}

# Archive types that can be inspected
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z"}

# Image types for preview
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

# ═══════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════
DATABASE_PATH = os.getenv("DATABASE_PATH", "omega_titanium.db")
MAX_HASH_SIZE = 100 * 1024 * 1024  # 100MB max for hashing

# ═══════════════════════════════════════════════════════════
# BUSINESS LOGIC
# ═══════════════════════════════════════════════════════════
# Minimum rating to be considered "market ready"
MIN_MARKET_READY_RATING = 8

# Categories for assets
ASSET_CATEGORIES = [
    "Design Files",
    "3D Models",
    "eBooks",
    "Courses",
    "Templates",
    "Stock Media",
    "Code/Scripts",
    "Other",
]

# Sales platforms
PLATFORMS = [
    "Etsy",
    "Creative Market",
    "Gumroad",
    "ThemeForest",
    "CodeCanyon",
    "GraphicRiver",
    "Udemy",
    "Amazon",
    "Manual Sale",
    "Other",
]

# Task priorities
TASK_PRIORITIES = ["Low", "Medium", "High", "Urgent"]

# Task statuses (Kanban columns)
TASK_STATUSES = {
    "ideas": "💡 Ideas",
    "todo": "📋 To Do",
    "in_progress": "⚡ In Progress",
    "done": "✅ Done",
}

# Asset statuses
ASSET_STATUSES = [
    "pending",   # Waiting for review
    "approved",  # Approved by both users
    "rejected",  # Rejected
    "listed",    # Listed for sale
    "sold",      # Sold
]

# ═══════════════════════════════════════════════════════════
# REMINDERS & AUTOMATION
# ═══════════════════════════════════════════════════════════
REMINDERS = {
    "weekly_review": {
        "enabled": True,
        "day": "Sunday",
        "time": "20:00",
        "message": "⏰ Weekly Review Time! Погледнете новите активи.",
    },
    "listing_alert": {
        "enabled": True,
        "threshold": 3,  # Alert when 3+ items approved
        "message": "🔔 Имате {count} одобрени активи готови за качване!",
    },
}

# ═══════════════════════════════════════════════════════════
# AI ROUTER CONFIGURATION (INTEGRATED)
# ═══════════════════════════════════════════════════════════
# Enable/disable AI Router features
ENABLE_AI_ROUTER = True
ENABLE_OLLAMA_FALLBACK = True
ENABLE_WEB_FALLBACK = True

# Web search limits
MAX_WEB_CALLS_PER_BATCH = 50

# AI Router logging
AI_ROUTER_LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Batch processing (for free tier)
FILES_PER_BATCH = 15  # Gemini free tier: 15 requests/minute
BATCH_DELAY = 60  # Seconds to wait between batches

# File type support (AI Router)
SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
SUPPORTED_DOCUMENT_TYPES = ['.pdf', '.docx', '.txt', '.md']
SUPPORTED_SPREADSHEET_TYPES = ['.xlsx', '.csv', '.xls']
SUPPORTED_AUDIO_TYPES = ['.mp3', '.wav', '.m4a', '.flac']
SUPPORTED_VIDEO_TYPES = ['.mp4', '.avi', '.mov', '.mkv']

# ═══════════════════════════════════════════════════════════
# UI SETTINGS
# ═══════════════════════════════════════════════════════════
APP_TITLE = "OMEGA v4 TITANIUM PRO"
APP_ICON = "💎"
THEME_COLOR = "#6c5ce7"  # Purple accent
PAGE_LAYOUT = "wide"

# Navigation menu structure
MENU_ITEMS = [
    "🏠 Dashboard",
    "🔍 Scanner",
    "📚 Library",
    "✅ Review Queue",
    "📋 Project Board",
    "💬 AI Assistant",
    "💰 Finances",
    "🏷️ Collections",
    "💡 Business Lab",
    "⚙️ Settings",
]
