# 📘 OMEGA v4 TITANIUM - USER GUIDE

## 🚀 COMPLETE WORKFLOW GUIDE

---

## 1️⃣ **FIRST TIME SETUP**

### **Installation:**
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.template .env
# Edit .env and add your GEMINI_API_KEY

# Run app
streamlit run app.py
```

### **Initial Login:**
- **Username:** Shadow or Maria
- **Password:** Set in `.env` file
- Default: `shadow123` / `maria123` (CHANGE THESE!)

---

## 2️⃣ **MODULE-BY-MODULE GUIDE**

### **🏠 DASHBOARD**

**What it shows:**
- 💰 Inventory Value (total estimated worth)
- 💵 Total Sales (all-time revenue)
- 📅 This Month (current month sales)
- 🚀 Ready to List (approved assets count)
- 📊 Charts (category breakdown, ratings)
- 📢 Recent Activity (who did what)

**When to use:**
- First thing every morning
- Check overall business health
- See what teammates are doing

---

### **🔍 SCANNER**

**Step-by-step:**

1. **Select Zone:**
   - Choose from dropdown (D:/, F:/, External)
   - Make sure drive is connected

2. **Choose Options:**
   - ✅ Scan Archives (ZIP/RAR files)
   - ✅ Scan Design Files (.psd, .ai)
   - ✅ Scan All File Types (everything allowed)

3. **Set Limit:**
   - Slider: Max files (10-500)
   - Start with 100 for first scan

4. **Click START DEEP SCAN:**
   - Progress bar shows scanning
   - AI analyzes each file automatically
   - Duplicates are skipped (hash checking)
   - New assets go to Review Queue

**AI Analysis includes:**
- Category (Design, 3D, eBook, etc.)
- Rating (1-10 market potential)
- Suggested Price ($)
- Best Platform (Etsy, Gumroad, etc.)
- Keywords for SEO
- Summary description

**Tips:**
- Scan one drive at a time
- Review results before next scan
- AI takes ~2-3 seconds per file

---

### **📚 LIBRARY**

**What it shows:**
- All scanned assets
- Filter by Category, Status
- Search by name or keywords

**For each asset you see:**
- Name, Category, Rating (stars)
- Price, Platform, Status
- Review status (Shadow ✅/⏳, Maria ✅/⏳)
- Keywords and AI summary

**Actions:**
- 📋 Details - Full asset info
- 📂 Open Folder - Opens file location
- View SEO Pack (if generated)

**Use cases:**
- Browse what you have
- Find specific assets
- Check approval status
- Quick reference

---

### **✅ REVIEW QUEUE**

**The Approval Workflow:**

**For each pending asset:**

1. **Shadow reviews first:**
   - Reads AI analysis
   - Adds optional note
   - Clicks ✅ APPROVE or ❌ REJECT

2. **Maria reviews:**
   - Sees Shadow's decision
   - Adds her note
   - Makes final call

3. **Both approved?**
   - Status → "approved"
   - Ready for Project Board
   - Can be listed for sale

**Additional actions:**
- 📝 Generate SEO - Creates title, description, tags

**Tips:**
- Review together for faster decisions
- Use notes to communicate
- Generate SEO after approval

---

### **📋 PROJECT BOARD (Kanban)**

**4 Columns:**

**💡 Ideas**
- AI suggestions
- Brainstorm projects
- Future plans

**📋 To Do**
- Ready to start
- Prioritized tasks
- Move from Ideas when ready

**⚡ In Progress**
- Currently working on
- Assigned tasks
- Active projects

**✅ Done**
- Completed tasks
- Archived automatically
- Track accomplishments

**How to use:**

1. **Add Task:**
   - Click ➕ Add New Task
   - Title + description
   - Set priority (Low/Medium/High/Urgent)
   - Assign to Shadow/Maria/Both

2. **Move Tasks:**
   - Click → button to advance
   - Tasks flow: Ideas → To Do → In Progress → Done

3. **AI Auto-Tasks:**
   - AI Assistant adds tasks automatically
   - Based on approved assets
   - From business consultant suggestions

**Task Sources:**
- Manual creation
- AI Consultant chat
- Asset approval (auto SEO tasks)

---

### **💬 AI ASSISTANT (Business Consultant)**

**What you can ask:**

**Strategy:**
- "How should I price my logo bundle?"
- "What assets should I focus on selling first?"
- "Create a marketing plan for this month"

**Bundle Suggestions:**
- "I have 10 logos. How should I bundle them?"
- "What collections make sense from my inventory?"

**Market Research:**
- "What's the demand for 3D car models?"
- "Where should I sell design templates?"

**Task Planning:**
- "Create tasks for launching on Etsy"
- "What should we work on this week?"

**AI will:**
- Analyze your current inventory
- Suggest specific actions
- Auto-add tasks to Project Board
- Provide market insights

**Example conversation:**
```
You: "We have 15 approved assets. What should we do?"

AI: "Great! I see you have:
- 8 Design templates (avg rating 9/10)
- 5 3D models (avg rating 8/10)
- 2 eBooks (rating 7/10)

Recommendation:
1. Bundle the 8 design templates → "Ultimate Design Pack" ($45)
2. List 3D models individually on Gumroad ($12 each)
3. Use eBooks as lead magnets (free for email signup)

I've added 5 tasks to your To Do board:
✅ Create design bundle ZIP
✅ Write Etsy description
✅ Create preview mockups
✅ Set up Gumroad listings
✅ Create landing page for email list"
```

---

### **💰 FINANCES**

**4 Main Metrics:**
- **💎 Inventory Value** - Total $ value of all assets
- **💰 Total Sales** - All-time revenue
- **📅 This Month** - Current month sales
- **📈 Projected** - Estimated monthly income

**Record a Sale:**

1. Click **➕ Add Sale**
2. Select asset from dropdown
3. Enter:
   - Platform (Etsy, Gumroad, etc.)
   - Sale Price ($)
   - Buyer Country (optional)
   - Notes (optional)
4. Click **💰 Record Sale**
5. Asset automatically marked as "sold"
6. Metrics update instantly

**Sales History:**
- Table view of all sales
- Filter by date, platform
- Export to CSV

**Use for:**
- ROI tracking
- Tax records
- Performance analysis

---

### **🏷️ COLLECTIONS (Bundles)**

**Why Create Collections:**
- Higher prices (bundle discount)
- Better conversion rates
- Easier marketing
- Customers love bundles

**How to Create:**

1. Click **➕ Create New Collection**
2. Name it (e.g., "Minimal Logo Pack")
3. Write description
4. Set target price
5. Select assets (multiselect)
6. Click **📦 Create Collection**

**Collection Status:**
- **Planning** - Still organizing
- **Ready** - Complete, needs listing
- **Listed** - Live for sale
- **Sold** - Completed sale

**Example Collections:**
- "Ultimate 3D Car Bundle" (20 models)
- "Beginner's Design Template Pack"
- "Complete eBook Bundle"

---

### **⚙️ SETTINGS**

**📁 Zones:**
- View all scanning zones
- Check which drives are accessible
- See status (Active/Offline)

**⏰ Reminders:**
- Weekly review reminder
- Listing alerts (when X assets approved)

**📊 Export:**
- Export all assets (CSV)
- Export sales history (CSV)
- Database backup

---

## 3️⃣ **DAILY WORKFLOW**

### **Morning Routine (5 mins):**
1. Check 🏠 **Dashboard** - See overnight activity
2. Review 💰 **Finances** - Any new sales?
3. Check ✅ **Review Queue** - New assets to approve?

### **Weekly Deep Work (1-2 hours):**

**Monday:**
- 🔍 **Scanner** - Scan new drives/folders
- ✅ **Review Queue** - Approve new assets together

**Wednesday:**
- 💬 **AI Assistant** - Strategic planning chat
- 📋 **Project Board** - Move tasks forward

**Friday:**
- 🏷️ **Collections** - Create new bundles
- 💰 **Finances** - Record any sales
- 📊 Check weekly progress

### **Monthly Tasks:**
- Export financial data (taxes)
- Review what's selling best
- Adjust pricing strategy
- Plan next month's focus

---

## 4️⃣ **PRO TIPS**

### **Scanning:**
✅ Start with smallest drive first
✅ Use 100 file limit initially
✅ Review before scanning more
❌ Don't scan C: drive (blocked)
❌ Avoid system folders

### **Approval Workflow:**
✅ Review together (faster)
✅ Use notes for communication
✅ Generate SEO after both approve
❌ Don't approve low-quality (rating <7)

### **Project Board:**
✅ Break big tasks into smaller ones
✅ Use priority levels
✅ Let AI suggest tasks
❌ Don't let To Do pile up (>20 tasks)

### **Collections:**
✅ Bundle similar themes
✅ 3-10 items per bundle (sweet spot)
✅ Price bundles 30-40% off individual
❌ Don't mix unrelated categories

### **AI Assistant:**
✅ Ask specific questions
✅ Provide context
✅ Let it add tasks automatically
❌ Don't ignore suggestions

---

## 5️⃣ **TROUBLESHOOTING**

### **"Drive not accessible"**
→ Make sure drive is connected
→ Check path in config.py
→ Try different USB port

### **"AI not responding"**
→ Check .env has GEMINI_API_KEY
→ Verify API key is valid
→ Check internet connection

### **"Can't approve asset"**
→ Make sure both users review
→ Check database isn't locked
→ Refresh page

### **"Scan too slow"**
→ Reduce max files limit
→ Skip large archives (>500MB)
→ Use faster storage (SSD)

---

## 6️⃣ **KEYBOARD SHORTCUTS**

(Streamlit default shortcuts)

- `Ctrl + R` - Rerun app
- `Ctrl + Shift + R` - Clear cache
- `Ctrl + /` - Focus search

---

## 7️⃣ **BEST PRACTICES**

### **Data Management:**
- Backup database weekly
- Export sales monthly
- Keep .env file secure

### **Team Collaboration:**
- Set review time together (e.g., Sunday 8pm)
- Use Project Board for communication
- Check Activity Feed daily

### **Business Growth:**
- Focus on high-rating assets first (9-10)
- Create bundles regularly
- Track what sells best
- Adjust prices based on sales data

---

**Need Help?**
- Check README.md for setup
- Review this guide for workflows
- Check system_log.json for errors

---

**OMEGA v4 TITANIUM User Guide** | v4.0.0
