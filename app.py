"""
╔═══════════════════════════════════════════════════════════════════╗
║                    OMEGA v4 TITANIUM                              ║
║          Complete Business Intelligence System                    ║
║                                                                   ║
║  Created for: Shadow & Leksy                                      ║
║  Purpose: Digital Asset Business Management                       ║
║  Features: AI Analysis, Multi-Drive Scan, Collaboration,         ║
║            Project Board, Financial Tracking, Collections         ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# Import custom modules
import config
import database
import security
import scanner
import ai_engine
import ui_components
import subprocess
import sys
import streamlit.components.v1 as components

import time

# Reviewer usernames (configurable via .env)
USER1 = config.REVIEW_USER_1_NAME
USER2 = config.REVIEW_USER_2_NAME

# ═══════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.PAGE_LAYOUT,
    initial_sidebar_state="expanded",
)
# ═══════════════════════════════════════════════════════════
# AUTHENTICATION
# ════

if not security.check_password():
    st.stop()

# ═══════════════════════════════════════════════════════════
# Load UI styles (след login)
# # ═══════════════════════════════════════════════════════════
ui_components.load_global_styles()

# Initialize database
conn = database.init_db(config.DATABASE_PATH)

# ═══════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════
if "current_zone" not in st.session_state:
    st.session_state.current_zone = list(config.ALLOWED_ZONES.keys())[0]
if "path" not in st.session_state:
    st.session_state.path = str(config.ALLOWED_ZONES[st.session_state.current_zone])
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = None

# ═══════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.title(f"{config.APP_ICON} {config.APP_TITLE}")

    # User info
    current_user = security.get_current_user()
    # Admin: notify on new logins
    try:
        security.notify_new_logins(
            conn, current_user=current_user, is_admin=security.is_admin_user()
        )
    except Exception:
        pass

    st.markdown(f"**👤 Logged in as:** {st.session_state.display_name}")

    st.markdown("---")

    # Navigation menu
    menu = st.radio("📍 Navigation", config.MENU_ITEMS, label_visibility="collapsed")

    st.markdown("---")

    # Quick stats (sidebar)
    stats = database.get_financial_stats(conn)
    st.metric("💎 Inventory Value", f"${stats['inventory_value']:.0f}")
    st.metric("✅ Ready to List", stats["ready_to_list"])

    st.markdown("---")

    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        security.logout()

# ═══════════════════════════════════════════════════════════
# MODULE 1: DASHBOARD
# ═══════════════════════════════════════════════════════════
if menu == "🏠 Dashboard":
    st.title("🏠 Business Intelligence Dashboard")

    # Get statistics
    stats = database.get_financial_stats(conn)
    df_assets = pd.read_sql("SELECT * FROM assets", conn)

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ui_components.render_metric_card(
            "Inventory Value", f"${stats['inventory_value']:.0f}", "💰"
        )

    with col2:
        ui_components.render_metric_card(
            "Total Sales", f"${stats['total_sales']:.0f}", "💵"
        )

    with col3:
        ui_components.render_metric_card(
            "This Month", f"${stats['month_sales']:.0f}", "📅"
        )

    with col4:
        ui_components.render_metric_card("Ready to List", stats["ready_to_list"], "🚀")

    st.markdown("---")

    # Charts row
    if not df_assets.empty:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("📊 Assets by Category")
            category_counts = df_assets["category"].value_counts()
            st.bar_chart(category_counts)

        with col_chart2:
            st.subheader("⭐ Rating Distribution")
            rating_counts = df_assets["rating"].value_counts().sort_index()
            st.line_chart(rating_counts)

    st.markdown("---")

    # Approval status
    col_status1, col_status2 = st.columns(2)

    with col_status1:
        st.subheader("✅ Approval Status")
        if not df_assets.empty:
            pending = len(df_assets[df_assets["status"] == "pending"])
            approved = len(df_assets[df_assets["status"] == "approved"])
            listed = len(df_assets[df_assets["status"] == "listed"])
            sold = len(df_assets[df_assets["status"] == "sold"])

            status_df = pd.DataFrame(
                {
                    "Status": ["⏳ Pending", "✅ Approved", "🚀 Listed", "💰 Sold"],
                    "Count": [pending, approved, listed, sold],
                }
            )
            st.dataframe(status_df, hide_index=True, use_container_width=True)

    with col_status2:
        st.subheader("📢 Recent Activity")
        recent_activity = database.get_recent_activity(conn, limit=5)

        if not recent_activity.empty:
            for _, row in recent_activity.iterrows():
                ui_components.render_activity_item(
                    row.get("user", "System"),
                    row.get("action", ""),
                    row.get("details", ""),
                    row.get("timestamp", ""),
                )
        else:
            st.info("No recent activity")

# ═══════════════════════════════════════════════════════════
# MODULE 2: SCANNER
# ══════════════════════════════
elif menu == "🔍 Scanner":
    st.title("🔍 Multi-Drive Smart Scanner")

    # Zone selector
    col_zone, col_action = st.columns([3, 1])

    with col_zone:
        selected_zone = st.selectbox(
            "📁 Select Zone to Scan",
            list(config.ALLOWED_ZONES.keys()),
            key="zone_selector",
        )
        current_base = config.ALLOWED_ZONES[selected_zone]

    with col_action:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 Get Statistics", use_container_width=True):
            with st.spinner("Analyzing directory..."):
                stats = scanner.get_scan_statistics(current_base, current_base)
                if "error" not in stats:
                    st.success(
                        f"✅ Found {stats['total_files']} files ({stats['total_size_gb']:.2f} GB)"
                    )

    # Check if zone exists
    if not current_base.exists():
        st.error(f"❌ Zone not accessible: {current_base}")
        st.info("💡 Connect the drive or update the path in config.py")
        st.stop()

    st.markdown("---")

    # Scan options
    st.subheader("🎯 Scan Options")

    col_opt1, col_opt2, col_opt3 = st.columns(3)

    with col_opt1:
        scan_archives = st.checkbox("📦 Scan Archives (ZIP/RAR/7z)", value=True)
    with col_opt2:
        scan_designs = st.checkbox("🎨 Scan Design Files", value=True)
    with col_opt3:
        scan_all = st.checkbox("🔍 Scan All Allowed Types", value=False)

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        batch_size = st.slider(
            "Batch size",
            5,
            50,
            20,
            help="How many NEW files to queue before analyzing.",
        )
    with col_t2:
        sleep_per_ai = st.slider(
            "Sleep per AI call (seconds)",
            1.0,
            10.0,
            4.5,
            0.5,
            help="Controls API rate to stay within free-tier limits.",
        )
    with col_t3:
        show_jobs = st.checkbox("Show scan job history", value=True)

    # Determine file types to scan
    file_types = set()
    if scan_archives:
        file_types.update(config.ARCHIVE_EXTENSIONS)
    if scan_designs:
        file_types.update({".psd", ".ai", ".eps", ".sketch", ".fig"})
    if scan_all:
        file_types = None  # None means "all allowed" in iter_scan_files()

    if not file_types and not scan_all:
        st.warning("⚠️ Select at least one scan option!")
    else:
        st.markdown("---")
        st.subheader("🚀 Background Scan Agent")

        # Active job panel (last job)
        active_job_id = st.session_state.get("active_scan_job_id")

        cols = st.columns([2, 1, 1])
        with cols[0]:
            start_clicked = st.button(
                "🚀 START (Background)", type="primary", use_container_width=True
            )
        with cols[1]:
            refresh_clicked = st.button("🔄 Refresh status", use_container_width=True)
        with cols[2]:
            stop_clicked = st.button(
                "🛑 Stop job",
                use_container_width=True,
                disabled=not bool(active_job_id),
            )

        if start_clicked:
            # Create job row
            job_id = database.create_scan_job(
                conn,
                zone=selected_zone,
                base_path=current_base,
                file_types=file_types if file_types is not None else None,
                created_by=current_user,
            )
            st.session_state.active_scan_job_id = job_id

            # Spawn worker process (doesn't block Streamlit)
            worker = Path(__file__).parent / "scan_worker.py"
            cmd = [
                sys.executable,
                str(worker),
                "--job-id",
                str(job_id),
                "--batch-size",
                str(batch_size),
                "--sleep-per-ai",
                str(sleep_per_ai),
            ]

            try:
                subprocess.Popen(cmd, cwd=str(Path(__file__).parent))
                st.success(
                    f"✅ Scan started in background (Job #{job_id}). You can switch tabs; it keeps running."
                )
            except Exception as e:
                database.set_scan_job_status(conn, job_id, "error", last_error=str(e))
                st.error(f"Failed to start background worker: {e}")

        if stop_clicked and active_job_id:
            database.request_stop_scan_job(conn, active_job_id)
            st.warning("Stop requested. The worker will stop after the current file.")

        # Status panel
        job_id = st.session_state.get("active_scan_job_id")
        if job_id:
            job = database.get_scan_job(conn, job_id)
            if job:
                status = job.get("status")
                processed = int(job.get("processed") or 0)
                skipped = int(job.get("skipped") or 0)
                errors = int(job.get("errors") or 0)
                total = int(job.get("total_candidates") or 0)
                seen = int(job.get("seen_files") or 0)

                pct = 0.0
                if total > 0:
                    pct = min(1.0, processed / total)

                st.markdown("### 📡 Live Status")
                st.progress(pct)
                st.write(
                    f"**Status:** `{status}` | "
                    f"**Processed:** {processed} | **Skipped:** {skipped} | **Errors:** {errors} | "
                    f"**Seen:** {seen} | **Total candidates:** {total}"
                )
                current_file = job.get("current_file")
                if current_file:
                    st.caption(f"Current file: {current_file}")

                if job.get("last_error"):
                    st.error(f"Last error: {job.get('last_error')}")

                # Auto-refresh while running (every ~2s)
                if status in ("queued", "running"):
                    st.caption("Auto-refresh is ON while the job is running.")
            components.html("<meta http-equiv='refresh' content='2'>", height=0)
        
        # Scanner Log Display
        st.markdown("---")
        st.subheader("📋 Scanner Processing Log")
        
        log_tab1, log_tab2 = st.tabs(["📊 Current Scan", "📜 Recent Activity"])
        
        with log_tab1:
            if job_id:
                # Try to get logs for current scan session
                # Session ID format: scan_{job_id}_{timestamp}
                c = conn.cursor()
                session_logs = c.execute(
                    """
                    SELECT * FROM scanner_log 
                    WHERE scan_session_id LIKE ?
                    ORDER BY scanned_at DESC 
                    LIMIT 50
                    """,
                    (f"scan_{job_id}_%",)
                ).fetchall()
                
                if session_logs:
                    logs_df = pd.DataFrame([dict(row) for row in session_logs])
                    
                    # Summary stats
                    summary = database.get_scan_summary(conn, logs_df.iloc[0]['scan_session_id'])
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    with col_s1:
                        st.metric("Total", summary['total'])
                    with col_s2:
                        st.metric("✅ Added", summary['added'])
                    with col_s3:
                        st.metric("⏭️ Skipped", summary['skipped'])
                    with col_s4:
                        st.metric("❌ Errors", summary['errors'])
                    
                    # Show log table
                    display_cols = ['file_name', 'action', 'status', 'scanned_at']
                    if 'error_message' in logs_df.columns:
                        # Only show error message if there are any
                        if logs_df['error_message'].notna().any():
                            display_cols.append('error_message')
                    
                    st.dataframe(
                        logs_df[display_cols],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "action": st.column_config.TextColumn("Action", width="small"),
                            "status": st.column_config.TextColumn("Status", width="small"),
                        }
                    )
                else:
                    st.info("No processing log yet for this scan job")
            else:
                st.info("Start a scan to see processing logs")
        
        with log_tab2:
            # Show recent logs across all scans
            recent_logs = database.get_scan_logs(conn, limit=100)
            if recent_logs:
                logs_df = pd.DataFrame(recent_logs)
                
                # Color code by status
                display_cols = ['zone_name', 'file_name', 'action', 'status', 'scanned_at']
                st.dataframe(
                    logs_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No scan history yet")

        if show_jobs:
            st.markdown("---")
            st.subheader("🗂️ Scan Jobs (history)")
            try:
                df_jobs = database.list_scan_jobs(conn, limit=30)
                # compact columns
                cols = [
                    "id",
                    "zone",
                    "status",
                    "started_at",
                    "finished_at",
                    "processed",
                    "skipped",
                    "errors",
                    "total_candidates",
                ]
                existing = [c for c in cols if c in df_jobs.columns]
                st.dataframe(
                    df_jobs[existing], use_container_width=True, hide_index=True
                )
            except Exception as e:
                st.error(f"Jobs history unavailable: {e}")

# ═════════════════════════════
elif menu == "📚 Library":
    st.title("📚 Master Asset Library")

    # Filters
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        category_filter = st.selectbox(
            "Filter by Category", ["All"] + config.ASSET_CATEGORIES
        )

    with col_filter2:
        status_filter = st.selectbox(
            "Filter by Status", ["All"] + config.ASSET_STATUSES
        )

    with col_filter3:
        search_query = st.text_input("🔍 Search assets...")

    # Load assets
    df = pd.read_sql("SELECT * FROM assets ORDER BY date_added DESC", conn)

    # Apply filters
    if category_filter != "All":
        df = df[df["category"] == category_filter]

    if status_filter != "All":
        df = df[df["status"] == status_filter]

    if search_query:
        df = df[
            df["name"].str.contains(search_query, case=False, na=False)
            | df["keywords"].str.contains(search_query, case=False, na=False)
        ]

    st.markdown(f"**Showing {len(df)} assets**")
    st.markdown("---")

    # Display assets
    if not df.empty:
        for _, row in df.iterrows():
            col_card, col_actions = st.columns([4, 1])

            with col_card:
                

                ui_components.render_asset_card(row)

            with col_actions:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button(
                    "📋 Details", key=f"details_{row['id']}", use_container_width=True
                ):
                    st.session_state.selected_asset = row["id"]

                if st.button(
                    "📂 Open Folder",
                    key=f"folder_{row['id']}",
                    use_container_width=True,
                ):
                    import os

                    try:
                        folder = Path(row["path"]).parent
                        os.startfile(folder)
                        st.success("✅ Folder opened!")
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("No assets found. Use Scanner to add assets.")

    # Asset details modal
    if st.session_state.selected_asset:
        st.markdown("---")
        st.subheader("📋 Asset Details")

        asset = df[df["id"] == st.session_state.selected_asset].iloc[0]

        col_det1, col_det2 = st.columns(2)

        with col_det1:
            st.markdown(f"**Name:** {asset['name']}")
            st.markdown(f"**Category:** {asset['category']}")
            st.markdown(f"**Rating:** {asset['rating']}/10 ⭐")
            st.markdown(f"**Price:** {asset['ai_price']}")
            st.markdown(f"**Platform:** {asset['platform']}")

        with col_det2:
            st.markdown(f"**Status:** {asset['status']}")
            
            # Get review status from new system
            review_status = database.get_review_status_display(conn, asset['id'])
            for reviewer, status in review_status.items():
                st.markdown(f"**{reviewer}:** {status}")
            
            st.markdown(f"**Added:** {asset['date_added']}")

        st.markdown(f"**Summary:** {asset['summary']}")
        st.markdown(f"**Keywords:** {asset['keywords']}")

        if asset["seo_pack"]:
            with st.expander("📝 SEO Content"):
                st.text(asset["seo_pack"])

        if st.button("❌ Close Details"):
            st.session_state.selected_asset = None
            st.rerun()

# ═══════════════════════════════════════════════════════════
# MODULE 4: REVIEW QUEUE (Approval Workflow)
# ═══════════════════════════════════════════════════════════
elif menu == "✅ Review Queue":
    st.title("✅ Asset Review Queue")

    st.markdown(f"**Reviewer:** {st.session_state.display_name}")

    # Load assets that need review (new system logic)
    # An asset needs review if:
    # 1. It's pending or approved status
    # 2. Current user hasn't reviewed it yet
    c = conn.cursor()
    
    # Get all pending/approved assets
    df_assets = pd.read_sql(
        """
        SELECT * FROM assets 
        WHERE status IN ('pending', 'approved')
        ORDER BY date_added DESC
        """,
        conn,
    )
    
    # Filter to only show assets where current user hasn't reviewed
    pending_for_user = []
    for _, asset in df_assets.iterrows():
        reviews = database.get_asset_reviews(conn, asset['id'])
        user_reviewed = any(r['reviewer_name'] == current_user for r in reviews)
        if not user_reviewed:
            pending_for_user.append(asset)
    
    df_pending = pd.DataFrame(pending_for_user)

    if df_pending.empty:
        st.success("🎉 No assets pending review!")
        st.info("All caught up! Check Scanner for new assets.")
    else:
        st.info(f"📋 {len(df_pending)} assets waiting for review")

        for _, asset in df_pending.iterrows():
            st.markdown("---")

            col_preview, col_review = st.columns([2, 1])

            with col_preview:
                ui_components.render_asset_card(asset)

                # Show reviews from other users (new system)
                all_reviews = database.get_asset_reviews(conn, asset['id'])
                for review in all_reviews:
                    if review['reviewer_name'] != current_user:
                        status_icon = '✅' if review['decision'] == 'approved' else '❌'
                        note_text = review['note'] or 'No note'
                        st.info(f"{status_icon} **{review['reviewer_name']}:** {note_text}")

            with col_review:
                st.markdown("### 🎯 Your Review")

                # Check if current user already reviewed (new system)
                all_reviews = database.get_asset_reviews(conn, asset['id'])
                user_review = next((r for r in all_reviews if r['reviewer_name'] == current_user), None)
                
                if user_review:
                    st.success(f"✅ You already reviewed this: {user_review['decision']}")
                else:
                    note = st.text_area(
                        "Add note (optional)", key=f"note_{asset['id']}"
                    )

                    col_approve, col_reject = st.columns(2)

                    with col_approve:
                        if st.button(
                            "✅ APPROVE",
                            key=f"app_{asset['id']}",
                            type="primary",
                            use_container_width=True,
                        ):
                            database.update_asset_review(
                                conn, asset["id"], current_user, True, note
                            )
                            st.success("Approved!")
                            st.rerun()

                    with col_reject:
                        if st.button(
                            "❌ REJECT",
                            key=f"rej_{asset['id']}",
                            use_container_width=True,
                        ):
                            database.update_asset_review(
                                conn, asset["id"], current_user, False, note
                            )
                            st.warning("Rejected")
                            st.rerun()

                    # Generate SEO button
                    if st.button(
                        "📝 Generate SEO",
                        key=f"seo_{asset['id']}",
                        use_container_width=True,
                    ):
                        with st.spinner("Generating SEO..."):
                            analysis = {
                                "category": asset["category"],
                                "summary": asset["summary"],
                                "keywords": asset["keywords"],
                            }
                            seo = ai_engine.generate_seo_pack(analysis, asset["name"])

                            # Save SEO
                            c = conn.cursor()
                            c.execute(
                                "UPDATE assets SET seo_pack=? WHERE id=?",
                                (seo, asset["id"]),
                            )
                            conn.commit()

                            st.text_area("SEO Generated:", seo, height=300)

# ═══════════════════════════════════════════════════════════
# MODULE 5: PROJECT BOARD (Kanban)
# ═══════════════════════════════════════════════════════════
elif menu == "📋 Project Board":
    st.title("📋 Project Board - Kanban Style")

    # Add new task
    with st.expander("➕ Add New Task"):
        task_title = st.text_input("Task Title")
        task_desc = st.text_area("Description")

        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            task_priority = st.selectbox("Priority", config.TASK_PRIORITIES)
        with col_t2:
            task_assigned = st.selectbox("Assign to", ["Both", USER1, USER2])
        with col_t3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Create Task", use_container_width=True):
                if task_title:
                    database.add_task(
                        conn,
                        task_title,
                        task_desc,
                        task_assigned,
                        task_priority,
                        created_by=current_user,
                    )
                    st.success("Task created!")
                    st.rerun()

    st.markdown("---")

    # Kanban columns
    col_ideas, col_todo, col_progress, col_done = st.columns(4)

    for col, (status_key, status_label) in zip(
        [col_ideas, col_todo, col_progress, col_done], config.TASK_STATUSES.items()
    ):
        with col:
            st.markdown(
                f"<div class='kanban-header'>{status_label}</div>",
                unsafe_allow_html=True,
            )

            # Load tasks for this column
            df_tasks = pd.read_sql(
                f"""
                SELECT * FROM tasks 
                WHERE status='{status_key}'
                ORDER BY 
                    CASE priority 
                        WHEN 'Urgent' THEN 1
                        WHEN 'High' THEN 2
                        WHEN 'Medium' THEN 3
                        WHEN 'Low' THEN 4
                    END,
                    date_added DESC
            """,
                conn,
            )

            if df_tasks.empty:
                st.info("No tasks")
            else:
                for _, task in df_tasks.iterrows():
                    ui_components.render_kanban_task(task)

                    # Task actions
                    col_a1, col_a2 = st.columns(2)

                    # Move buttons
                    if status_key != "done":
                        next_status = {
                            "ideas": "todo",
                            "todo": "in_progress",
                            "in_progress": "done",
                        }[status_key]

                        with col_a1:
                            if st.button(
                                "→", key=f"move_{task['id']}", use_container_width=True
                            ):
                                database.update_task_status(
                                    conn, task["id"], next_status, current_user
                                )
                                st.rerun()

                    with col_a2:
                        if st.button(
                            "🗑️", key=f"del_{task['id']}", use_container_width=True
                        ):
                            c = conn.cursor()
                            c.execute("DELETE FROM tasks WHERE id=?", (task["id"],))
                            conn.commit()
                            st.rerun()

# ═══════════════════════════════════════════════════════════
# MODULE 6: AI ASSISTANT (Chat)
# ═══════════════════════════════════════════════════════════
elif menu == "💬 AI Assistant":
    st.title("💬 AI Business Consultant")

    # Check for API key
    if not config.GEMINI_API_KEY:
        st.error("⚠️ API Key not configured!")
        st.info(
            """
        To use AI Assistant, you need to:
        1. Get a free API key from: https://aistudio.google.com/app/apikey
        2. Add it to your .env file: `GEMINI_API_KEY=your_key_here`
        3. Restart the application
        """
        )
        st.markdown("---")
        st.markdown("**See AI_ASSISTANT_SETUP_BG.md for detailed instructions**")
        st.stop()

    st.markdown(
        """
        <div style='background: rgba(255,255,255,0.9); padding: 16px; border-radius: 12px; margin-bottom: 20px;'>
        👋 Hi! I'm your AI Business Consultant. I can help you with:<br>
        • Analyzing your assets and suggesting strategies<br>
        • Creating bundles and collections<br>
        • Pricing recommendations<br>
        • Marketing ideas<br>
        • Adding tasks to your project board<br>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Clear chat button
    col_title, col_clear = st.columns([4, 1])
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # Chat history display
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    if not st.session_state.chat_history:
        # Show example questions when chat is empty
        st.markdown("### 💡 Try asking:")
        example_col1, example_col2 = st.columns(2)

        with example_col1:
            st.info(
                "• What should I focus on this week?\n• Analyze my current inventory\n• Suggest pricing for my top assets"
            )

        with example_col2:
            st.info(
                "• Create a marketing plan\n• What bundles should I create?\n• How can I increase sales?"
            )

    # Display chat history

    for msg in st.session_state.chat_history:
        ui_components.render_chat_message(msg["message"], is_user=True)
        ui_components.render_chat_message(msg["response"], is_user=False)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # User input with form for Enter key support
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "💬 Your question:",
            key="ai_chat_input",
            placeholder="Type your question and press Enter...",
            label_visibility="collapsed",
        )

        # Form submit button (hidden via CSS, but allows Enter to work)
        submit_button = st.form_submit_button("📤 Send", use_container_width=True)

    # Process input when form submitted
    if submit_button and user_input.strip():
        # Get context
        stats = database.get_financial_stats(conn)
        df_assets = pd.read_sql(
            "SELECT category, rating, ai_price FROM assets WHERE status='approved'",
            conn,
        )

        context = {
            "inventory_value": stats["inventory_value"],
            "ready_to_list": stats["ready_to_list"],
            "approved_assets_count": len(df_assets),
            "top_categories": (
                df_assets["category"].value_counts().head(3).to_dict()
                if not df_assets.empty
                else {}
            ),
        }

        # Get AI response
        with st.spinner("🤖 Thinking..."):
            ai_response = ai_engine.ai_business_consultant(user_input, context)

        # Save to history
        st.session_state.chat_history.append(
            {"message": user_input, "response": ai_response["response"]}
        )

        # Save to database
        database.save_ai_chat(conn, user_input, ai_response["response"], current_user)

        # Add suggested tasks
        if ai_response.get("suggested_tasks"):
            st.success(f"✅ AI suggested {len(ai_response['suggested_tasks'])} tasks")
            for task in ai_response["suggested_tasks"]:
                database.add_task(
                    conn,
                    task["title"],
                    task["description"],
                    "Both",
                    "Medium",
                    created_by="AI",
                )

        st.rerun()

# ═══════════════════════════════════════════════════════════
# MODULE 7: FINANCES
# ═══════════════════════════════════════════════════════════
elif menu == "💰 Finances":
    st.title("💰 Financial Analytics & Sales Tracking")

    # Financial overview
    stats = database.get_financial_stats(conn)

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        ui_components.render_metric_card(
            "Inventory Value", f"${stats['inventory_value']:.0f}", "💎"
        )

    with col_f2:
        ui_components.render_metric_card(
            "Total Sales", f"${stats['total_sales']:.0f}", "💰"
        )

    with col_f3:
        ui_components.render_metric_card(
            "This Month", f"${stats['month_sales']:.0f}", "📅"
        )

    with col_f4:
        # Projected monthly (estimate)
        approved_count = stats["ready_to_list"]
        projected = approved_count * 20 * 0.15  # Avg $20, 15% conversion
        ui_components.render_metric_card("Projected", f"${projected:.0f}", "📈")

    st.markdown("---")

    # Record new sale
    st.subheader("💵 Record New Sale")

    with st.expander("➕ Add Sale"):
        # Get approved assets
        df_listed = pd.read_sql(
            "SELECT id, name FROM assets WHERE status IN ('approved', 'listed')", conn
        )

        if df_listed.empty:
            st.info("No assets available to mark as sold")
        else:
            asset_choice = st.selectbox("Select Asset", df_listed["name"].tolist())
            asset_id = df_listed[df_listed["name"] == asset_choice]["id"].iloc[0]

            col_s1, col_s2 = st.columns(2)

            with col_s1:
                sale_platform = st.selectbox("Platform", config.PLATFORMS)
                sale_price = st.number_input(
                    "Sale Price ($)", min_value=0.0, value=10.0, step=1.0
                )

            with col_s2:
                buyer_country = st.text_input("Buyer Country (optional)")
                sale_notes = st.text_area("Notes (optional)")

            if st.button("💰 Record Sale", type="primary"):
                database.add_sale(
                    conn, asset_id, sale_platform, sale_price, buyer_country, sale_notes
                )
                st.success(f"✅ Sale recorded! +${sale_price}")
                st.balloons()
                st.rerun()

    st.markdown("---")

    # Sales history
    st.subheader("📊 Sales History")

    df_sales = pd.read_sql(
        """
        SELECT s.*, a.name as asset_name
        FROM sales s
        JOIN assets a ON s.asset_id = a.id
        ORDER BY s.sale_date DESC
    """,
        conn,
    )

    if not df_sales.empty:
        st.dataframe(
            df_sales[
                ["sale_date", "asset_name", "platform", "sale_price", "buyer_country"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No sales recorded yet. Start selling!")

# ═══════════════════════════════════════════════════════════
# MODULE 8: COLLECTIONS
# ═══════════════════════════════════════════════════════════
elif menu == "🏷️ Collections":
    st.title("🏷️ Collections & Bundles")

    # Create new collection
    with st.expander("➕ Create New Collection"):
        coll_name = st.text_input("Collection Name")
        coll_desc = st.text_area("Description")
        coll_price = st.number_input("Target Price ($)", min_value=0.0, value=25.0)

        # Select assets
        df_approved = pd.read_sql(
            "SELECT id, name, category FROM assets WHERE status='approved'", conn
        )

        if not df_approved.empty:
            selected_assets = st.multiselect(
                "Select Assets", df_approved["name"].tolist()
            )

            if st.button("📦 Create Collection", type="primary"):
                if coll_name and selected_assets:
                    asset_ids = [
                        int(df_approved[df_approved["name"] == name]["id"].iloc[0])
                        for name in selected_assets
                    ]
                    database.create_collection(
                        conn, coll_name, coll_desc, asset_ids, current_user
                    )
                    st.success("Collection created!")
                    st.rerun()
        else:
            st.info("No approved assets available")

    st.markdown("---")

    # Display collections
    st.subheader("📦 Your Collections")

    df_collections = pd.read_sql(
        "SELECT * FROM collections ORDER BY date_created DESC", conn
    )

    if not df_collections.empty:
        for _, coll in df_collections.iterrows():
            ui_components.render_collection_card(coll)

            # Show assets in collection
            asset_ids = json.loads(coll["asset_ids"])

            if asset_ids:
                assets_in_coll = pd.read_sql(
                    f"""
                    SELECT name, category, ai_price 
                    FROM assets 
                    WHERE id IN ({','.join(map(str, asset_ids))})
                """,
                    conn,
                )

                with st.expander(f"View {len(asset_ids)} assets"):
                    st.dataframe(
                        assets_in_coll, hide_index=True, use_container_width=True
                    )
    else:
        st.info("No collections yet. Create your first bundle!")

# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# MODULE 9: BUSINESS LAB (Ideas + Evaluation)
# ═══════════════════════════════════════════════════════════
elif menu == "💡 Business Lab":
    st.title("💡 Business Lab")
    st.caption("Create business ideas and run structured SaaS/market evaluations.")

    tab_ideas, tab_evaluate, tab_history = st.tabs(
        ["📝 Ideas", "📊 Evaluate", "🕘 History"]
    )

    with tab_ideas:
        st.subheader("📝 Create a new idea")
        with st.form("idea_create_form", clear_on_submit=True):
            title = st.text_input("Title *")
            sector = st.text_input("Sector / Industry")
            problem = st.text_area("Problem (what pain are we solving?)", height=90)
            solution = st.text_area("Solution (what are we building?)", height=90)
            target_customer = st.text_input("Target customer (ICP)")
            differentiator = st.text_input("Differentiator / Moat (why you?)")
            submitted = st.form_submit_button("➕ Add Idea", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                idea_id = database.add_business_idea(
                    conn,
                    title=title.strip(),
                    sector=sector.strip(),
                    problem=problem.strip(),
                    solution=solution.strip(),
                    target_customer=target_customer.strip(),
                    differentiator=differentiator.strip(),
                    created_by=current_user,
                )
                security.log_event(
                    "idea_created",
                    username=current_user,
                    details=f"idea_id={idea_id} | {title.strip()}",
                )
                st.success(f"✅ Idea created (ID {idea_id}).")
                st.rerun()

        st.markdown("---")
        st.subheader("📋 Ideas")
        df = database.list_business_ideas(conn)
        if df.empty:
            st.info("No ideas yet.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_evaluate:
        st.subheader("📊 Evaluate an idea")
        df = database.list_business_ideas(conn)
        if df.empty:
            st.info("Create an idea first.")
        else:
            options = {
                f"#{row['id']} — {row['title']}": int(row["id"])
                for _, row in df.iterrows()
            }
            selected_label = st.selectbox("Pick idea", list(options.keys()))
            idea_id = options[selected_label]

            # Pull idea row
            idea_row = df[df["id"] == idea_id].iloc[0].to_dict()

            # Add internal context (read-only snapshot)
            stats = database.get_financial_stats(conn)
            tasks_df = pd.read_sql(
                "SELECT status, priority, assigned_to FROM tasks", conn
            )
            context = {
                "inventory_value": stats.get("inventory_value"),
                "ready_to_list": stats.get("ready_to_list"),
                "total_sales": stats.get("total_sales"),
                "tasks_by_status": (
                    tasks_df["status"].value_counts().to_dict()
                    if not tasks_df.empty
                    else {}
                ),
            }

            st.markdown("**Idea details**")
            st.json(
                {
                    k: idea_row.get(k)
                    for k in [
                        "title",
                        "sector",
                        "problem",
                        "solution",
                        "target_customer",
                        "differentiator",
                    ]
                }
            )

            if st.button(
                "🤖 Run AI evaluation", type="primary", use_container_width=True
            ):
                with st.spinner("Evaluating..."):
                    result = ai_engine.evaluate_business_idea(idea_row, context=context)
                database.save_business_evaluation(
                    conn,
                    idea_id,
                    result.get("evaluation", {}),
                    result.get("model_used"),
                    current_user,
                )
                security.log_event(
                    "idea_evaluated",
                    username=current_user,
                    details=f"idea_id={idea_id} | model={result.get('model_used')}",
                )
                st.success("✅ Evaluation saved.")
                st.rerun()

            latest = database.get_latest_business_evaluation(conn, idea_id)
            if latest:
                st.markdown("---")
                st.subheader("Latest evaluation")
                st.caption(
                    f"Model: {latest.get('model_used')} | Time: {latest.get('created_at')}"
                )
                st.json(latest.get("evaluation"))

    with tab_history:
        st.subheader("🕘 Evaluation history")
        try:
            hist = pd.read_sql(
                "SELECT e.id, e.idea_id, i.title, e.model_used, e.created_by, e.created_at "
                "FROM business_evaluations e JOIN business_ideas i ON i.id=e.idea_id "
                "ORDER BY e.id DESC LIMIT 200",
                conn,
            )
            if hist.empty:
                st.info("No evaluations yet.")
            else:
                st.dataframe(hist, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"History unavailable: {e}")

# MODULE 9: SETTINGS
# ═══════════════════════════════════════════════════════════
elif menu == "⚙️ Settings":
    st.title("⚙️ System Settings")

    tab_zones, tab_reminders, tab_security, tab_export = st.tabs(
        ["📁 Zones", "⏰ Reminders", "🛡️ Security", "📊 Export"]
    )

    with tab_zones:
        st.subheader("📁 Scanning Zones")

        st.info("Configure which drives/folders the scanner can access")

        for zone_name, zone_path in config.ALLOWED_ZONES.items():
            col_z1, col_z2 = st.columns([3, 1])

            with col_z1:
                st.markdown(f"**{zone_name}**")
                st.caption(f"Path: {zone_path}")
                st.caption(
                    f"Status: {'✅ Accessible' if zone_path.exists() else '❌ Not found'}"
                )

            with col_z2:
                if zone_path.exists():
                    st.success("Active")
                else:
                    st.error("Offline")

    with tab_reminders:
        st.subheader("⏰ Reminders & Automation")

        st.markdown("**Weekly Review Reminder**")
        weekly_enabled = st.checkbox("Enable weekly review reminder", value=True)

        if weekly_enabled:
            st.info("📅 Set for: Sunday at 20:00")

        st.markdown("**Listing Alert**")
        listing_threshold = st.slider("Alert when X assets are approved", 1, 10, 3)
        st.info(f"🔔 Alert when {listing_threshold}+ assets ready to list")

    with tab_security:
        st.subheader("🛡️ Security Monitor")
        st.caption("Login attempts, audit events, and banlist (LAN-focused).")

        col_s1, col_s2 = st.columns([2, 1])

        with col_s1:
            st.markdown("### Recent events")
            df_events = database.get_security_events(conn, limit=200)
            if df_events.empty:
                st.info("No security events yet.")
            else:
                st.dataframe(df_events, use_container_width=True, hide_index=True)

        with col_s2:
            st.markdown("### Ban / Unban")
            ban_type = st.selectbox("Type", ["ip", "username"])
            ban_value = st.text_input("Value (IP or username)")
            ban_reason = st.text_input("Reason", value="security policy")

            if st.button("🚫 Ban", type="primary", use_container_width=True):
                if not ban_value.strip():
                    st.error("Value is required.")
                else:
                    security.ban_entity(
                        ban_type,
                        ban_value.strip(),
                        ban_reason.strip(),
                        banned_by=current_user,
                    )
                    st.success("Banned.")
                    st.rerun()

            if st.button("✅ Unban", use_container_width=True):
                if not ban_value.strip():
                    st.error("Value is required.")
                else:
                    security.unban_entity(
                        ban_type, ban_value.strip(), unbanned_by=current_user
                    )
                    st.success("Unbanned.")
                    st.rerun()

            st.markdown("---")
            st.markdown("### Banlist")
            df_bans = database.get_banned_entities(conn)
            if df_bans.empty:
                st.info("No bans.")
            else:
                st.dataframe(df_bans, use_container_width=True, hide_index=True)

    with tab_export:
        st.subheader("📊 Export Data")

        if st.button("📥 Export All Assets (CSV)", use_container_width=True):
            df_export = pd.read_sql("SELECT * FROM assets", conn)
            csv = df_export.to_csv(index=False)
            st.download_button(
                "Download CSV", csv, "omega_assets_export.csv", "text/csv"
            )

        if st.button("📥 Export Sales History (CSV)", use_container_width=True):
            df_sales_export = pd.read_sql("SELECT * FROM sales", conn)
            csv_sales = df_sales_export.to_csv(index=False)
            st.download_button(
                "Download Sales CSV", csv_sales, "omega_sales_export.csv", "text/csv"
            )

        st.markdown("---")

        st.subheader("🗄️ Database Info")

        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM assets")
        total_assets = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM collections")
        total_collections = c.fetchone()[0]

        st.info(
            f"""
        📊 **Database Statistics**
        - Assets: {total_assets}
        - Tasks: {total_tasks}
        - Collections: {total_collections}
        - Database: {config.DATABASE_PATH}
        """
        )

# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("---")
st.caption(
    f"OMEGA v4 TITANIUM | User: {st.session_state.display_name} | Session: Active ✅"
)
