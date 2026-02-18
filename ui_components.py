"""
OMEGA v4 TITANIUM - UI COMPONENTS
Modern glassmorphism design system (Titanium Dark)
"""

import streamlit as st
import config


def _reviewer_labels():
    """Return reviewer labels from config (dynamic, no hardcoded names)."""
    r1 = getattr(config, "REVIEW_USER_1_NAME", "Reviewer 1")
    r2 = getattr(config, "REVIEW_USER_2_NAME", "Reviewer 2")
    return r1, r2


def load_global_styles():
    """Load global CSS styles"""
    st.markdown(
        f"""
<style>
/* ═══════════════════════════════════════════════════════════ */
/* GLOBAL THEME (TITANIUM DARK) */
/* ═══════════════════════════════════════════════════════════ */
.stApp {{
    background:
        radial-gradient(1200px circle at 20% 10%, rgba(108, 92, 231, 0.25), transparent 40%),
        radial-gradient(900px circle at 80% 20%, rgba(116, 185, 255, 0.18), transparent 35%),
        #0f1117;
    color: #e6e6eb;
}}

h1, h2, h3, h4 {{
    color: #ffffff;
}}

p, span, label {{
    color: #e6e6eb;
}}

.stMarkdown, .stText, .stCaption, .stLabel {{
    color: #e6e6eb;
}}

/* ═══════════════════════════════════════════════════════════ */
/* SIDEBAR */
/* ═══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: #161a23 !important;
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: none !important;
}}

section[data-testid="stSidebar"] * {{
    color: #e6e6eb !important;
}}

section[data-testid="stSidebar"] a:hover {{
    color: {config.THEME_COLOR} !important;
}}

/* ═══════════════════════════════════════════════════════════ */
/* PREMIUM CARDS */
/* ═══════════════════════════════════════════════════════════ */
.omega-card {{
    background: rgba(22, 26, 35, 0.78);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 6px solid {config.THEME_COLOR};
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    margin: 0 0 20px 0;
    transition: all 0.3s ease;
    width: 100%;
    display: block;
}}

.omega-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
}}

/* Extra force inside Streamlit markdown container */
div[data-testid="stMarkdownContainer"] .omega-card {{
    background: rgba(22, 26, 35, 0.78) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-left: 6px solid {config.THEME_COLOR} !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35) !important;
    width: 100% !important;
    display: block !important;
}}

.omega-card, .omega-card p, .omega-card div, .omega-card span, .omega-card b {{
    color: #e6e6eb;
}}

/* ═══════════════════════════════════════════════════════════ */
/* METRIC CARDS */
/* ═══════════════════════════════════════════════════════════ */
.metric-card {{
    background: rgba(22, 26, 35, 0.65);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}}

.metric-value {{
    font-size: 2.5em;
    font-weight: bold;
    color: {config.THEME_COLOR};
    margin: 10px 0;
}}

.metric-label {{
    font-size: 0.9em;
    color: #9aa0ac;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ═══════════════════════════════════════════════════════════ */
/* STATUS BADGES */
/* ═══════════════════════════════════════════════════════════ */
.status-badge {{
    display: inline-block;
    padding: 6px 14px;
    border-radius: 50px;
    font-size: 0.75em;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.status-pending {{
    background: #f1c40f;
    color: #111318;
}}

.status-approved {{
    background: #2ecc71;
    color: #0b2b16;
}}

.status-listed {{
    background: #3498db;
    color: #071b29;
}}

.status-sold {{
    background: #e84393;
    color: #2a0716;
}}

.status-rejected {{
    background: #e74c3c;
    color: #2a0716;
}}

/* ═══════════════════════════════════════════════════════════ */
/* RATING STARS */
/* ═══════════════════════════════════════════════════════════ */
.rating-stars {{
    font-size: 1.2em;
    color: #f1c40f;
}}

/* ═══════════════════════════════════════════════════════════ */
/* ACTIVITY FEED */
/* ═══════════════════════════════════════════════════════════ */
.activity-item {{
    background: rgba(22, 26, 35, 0.65);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    border-left: 4px solid {config.THEME_COLOR};
    font-size: 0.9em;
    border: 1px solid rgba(255,255,255,0.06);
}}

.activity-user {{
    font-weight: bold;
    color: {config.THEME_COLOR};
}}

.activity-time {{
    color: #9aa0ac;
    font-size: 0.85em;
    float: right;
}}

/* ═══════════════════════════════════════════════════════════ */
/* KANBAN TASK */
/* ═══════════════════════════════════════════════════════════ */
.kanban-task {{
    background: rgba(15, 17, 23, 0.9);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
    border-left: 4px solid {config.THEME_COLOR};
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid rgba(255,255,255,0.06);
}}

.kanban-task:hover {{
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.65);
    transform: translateX(4px);
}}

/* ═══════════════════════════════════════════════════════════ */
/* CHAT */
/* ═══════════════════════════════════════════════════════════ */
.chat-container {{
    background: rgba(22, 26, 35, 0.85);
    border-radius: 20px;
    padding: 20px;
    max-height: 600px;
    overflow-y: auto;
    border: 1px solid rgba(255,255,255,0.08);
}}

.chat-message-user {{
    background: {config.THEME_COLOR};
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 70%;
    margin-left: auto;
    display: block;
}}

.chat-message-ai {{
    background: #1c2130;
    color: #e6e6eb;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 70%;
    border: 1px solid rgba(255,255,255,0.06);
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_metric_card(label, value, icon="📊"):
    st.markdown(
        f"""
<div class="metric-card">
  <div style="font-size: 2em;">{icon}</div>
  <div class="metric-value">{value}</div>
  <div class="metric-label">{label}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_asset_card(asset_row):
    """Render premium asset card (no hardcoded reviewer names)."""
    reviewer1, reviewer2 = _reviewer_labels()

    status = asset_row.get("status", "pending")
    status_class = f"status-{status}"
    status_text = str(status).upper()

    # Rating (0..10)
    try:
        rating = int(asset_row.get("rating", 5) or 5)
    except Exception:
        rating = 5
    rating = max(0, min(10, rating))
    stars = "⭐" * rating

    # ✅/⏳ (columns stay as-is; labels are dynamic)
    r1 = "✅" if asset_row.get("reviewed_by_shadow") else "⏳"
    r2 = "✅" if asset_row.get("reviewed_by_maria") else "⏳"

    name = asset_row.get("name") or "Unknown"
    summary = asset_row.get("summary") or "No description available"
    ai_price = asset_row.get("ai_price") or "N/A"
    platform = asset_row.get("platform") or "N/A"
    category = asset_row.get("category") or "Other"
    keywords = asset_row.get("keywords") or ""

    tags_preview = "—"
    if keywords:
        tags_preview = keywords[:30] + ("..." if len(keywords) > 30 else "")

    # 🔑 НЯМА водещи интервали / нов ред преди <div> (иначе Streamlit го показва като код)
    html = (
        f'<div class="omega-card">'
        f'  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">'
        f'    <span class="status-badge {status_class}">{status_text}</span>'
        f'    <span class="rating-stars">{stars} {rating}/10</span>'
        f'  </div>'
        f'  <h3 style="margin:12px 0; color:#ffffff;">{name}</h3>'
        f'  <p style="color:#9aa0ac; margin:12px 0; font-size:0.95em;">{summary}</p>'
        f'  <div style="border-top:1px solid rgba(255,255,255,0.08); padding-top:12px; margin-top:12px;">'
        f'    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.85em; color:#e6e6eb;">'
        f'      <div><b>💰 Price:</b> {ai_price}</div>'
        f'      <div><b>🏪 Platform:</b> {platform}</div>'
        f'      <div><b>📁 Category:</b> {category}</div>'
        f'      <div><b>🏷️ Tags:</b> {tags_preview}</div>'
        f'    </div>'
        f'  </div>'
        f'  <div style="margin-top:16px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.08);">'
        f'    <b>👥 Reviews:</b>'
        f'    <span style="margin-left:12px;">{reviewer1} {r1}</span>'
        f'    <span style="margin-left:12px;">{reviewer2} {r2}</span>'
        f'  </div>'
        f'</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def render_activity_item(user, action, details, timestamp):
    from datetime import datetime

    try:
        dt = datetime.fromisoformat(timestamp)
        time_str = dt.strftime("%H:%M")
    except Exception:
        time_str = "recently"

    emoji_map = {
        "login_success": "🔓",
        "asset_added": "📄",
        "asset_approved": "✅",
        "asset_rejected": "❌",
        "task_created": "📋",
        "task_updated": "⚡",
        "collection_created": "📦",
        "sale_recorded": "💰",
    }
    emoji = emoji_map.get(action, "📌")

    details_html = (
        f'<div style="margin-top:4px; color:#9aa0ac; font-size:0.9em;">{details}</div>'
        if details
        else ""
    )

    st.markdown(
        f"""
<div class="activity-item">
  <span class="activity-time">{time_str}</span>
  <span>{emoji}</span>
  <span class="activity-user">{user}</span>
  <span> {action.replace('_', ' ')}</span>
  {details_html}
</div>
""",
        unsafe_allow_html=True,
    )


def render_kanban_task(task_row):
    priority_colors = {
        "Low": "#95a5a6",
        "Medium": "#3498db",
        "High": "#e67e22",
        "Urgent": "#e74c3c",
    }

    reviewer1, reviewer2 = _reviewer_labels()

    priority = task_row.get("priority", "Medium")
    color = priority_colors.get(priority, "#3498db")

    assigned = task_row.get("assigned_to", "Both")
    assigned_emoji = "👤" if assigned in [reviewer1, reviewer2] else "👥"

    description_html = (
        f'<div style="font-size:0.85em; color:#9aa0ac; margin-bottom:8px;">{task_row.get("description","")}</div>'
        if task_row.get("description")
        else ""
    )

    st.markdown(
        f"""
<div class="kanban-task" style="border-left-color:{color};">
  <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
    <span style="font-weight:600; color:#ffffff;">{task_row.get('title', 'Untitled')}</span>
    <span>{assigned_emoji}</span>
  </div>
  {description_html}
  <div style="display:flex; justify-content:space-between; font-size:0.75em; color:#9aa0ac;">
    <span>{priority} priority</span>
    <span>{assigned}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_chat_message(message, is_user=True):
    css_class = "chat-message-user" if is_user else "chat-message-ai"
    icon = "👤" if is_user else "🤖"

    st.markdown(
        f"""
<div class="{css_class}">
  <span style="margin-right:8px;">{icon}</span>
  {message}
</div>
""",
        unsafe_allow_html=True,
    )


def render_collection_card(collection_row):
    status = collection_row.get("status", "planning")
    status_emoji = {"planning": "📝", "ready": "✅", "listed": "🚀", "sold": "💰"}.get(
        status, "📦"
    )
    description = collection_row.get("description", "No description")

    st.markdown(
        f"""
<div class="omega-card">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="color:#ffffff;">{status_emoji} {collection_row.get('name', 'Untitled Collection')}</h3>
    <span class="status-badge status-{status}">{status}</span>
  </div>

  <p style="color:#9aa0ac; margin:12px 0;">{description}</p>

  <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:16px; color:#e6e6eb;">
    <div><b>🎯 Target Price:</b> ${collection_row.get('target_price', 0)}</div>
    <div><b>👤 Created by:</b> {collection_row.get('created_by', 'Unknown')}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
