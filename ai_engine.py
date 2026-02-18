"""
OMEGA v4 TITANIUM (FREE-TIER SAFE)
- Single-file, copy-paste ready.
- No genai.list_models() (saves quota).
- 429-aware backoff (max 1 retry).
- Optional disk cache to avoid повторни заявки.
- Robust JSON extraction (handles markdown/text around JSON).
- Free-tier defaults: минимален брой модели, минимален брой retries.
"""

import json
import re
import time
import random
import hashlib
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
import config


# ─────────────────────────────────────────────────────────────
# CONFIG (SAFE DEFAULTS)
# ─────────────────────────────────────────────────────────────

FREE_TIER_MODE = True

# Cache folder (disable by setting to None)
CACHE_DIR = Path(getattr(config, "AI_CACHE_DIR", "ai_cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Hard cap to avoid model-spam on free tier
MAX_MODELS_TO_TRY = 2 if FREE_TIER_MODE else 5
MAX_RETRIES_429 = 1 if FREE_TIER_MODE else 3

DEFAULT_TIMEOUT = int(getattr(config, "AI_TIMEOUT", 25))
PRIMARY_MODEL = getattr(config, "PRIMARY_MODEL", "gemini-1.5-flash")
FALLBACK_MODEL = getattr(config, "FALLBACK_MODEL", "gemini-1.5-flash")


# Configure Gemini
if getattr(config, "GEMINI_API_KEY", None):
    genai.configure(api_key=config.GEMINI_API_KEY)
else:
    raise RuntimeError("FATAL: GEMINI_API_KEY not found in config.py")


# ─────────────────────────────────────────────────────────────
# MODEL MANAGEMENT (NO DISCOVERY CALLS)
# ─────────────────────────────────────────────────────────────

def _normalize_model_name(name: str) -> str:
    if not name:
        return ""
    return name.strip().replace("models/", "")

def model_candidates() -> list[str]:
    """
    Free-tier safe: do NOT call genai.list_models().
    Try minimal ordered candidates.
    """
    prefs: list[str] = []
    try:
        prefs.extend(getattr(config, "AI_MODEL_PREFERENCE", []) or [])
    except Exception:
        pass

    # Always include configured primary/fallback
    prefs.extend([PRIMARY_MODEL, FALLBACK_MODEL])

    # Optional survival list (keep short for free-tier)
    if not FREE_TIER_MODE:
        prefs.extend(["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"])
    else:
        prefs.extend(["gemini-1.5-flash"])

    seen = set()
    out: list[str] = []
    for p in prefs:
        p = _normalize_model_name(p)
        if p and p not in seen:
            seen.add(p)
            out.append(p)

    return out[:MAX_MODELS_TO_TRY]


# ─────────────────────────────────────────────────────────────
# ERROR HANDLING (429 BACKOFF)
# ─────────────────────────────────────────────────────────────

def _is_429(err: str) -> bool:
    e = err.lower()
    return ("429" in e) or ("quota exceeded" in e) or ("rate limit" in e)

def _quota_is_zero(err: str) -> bool:
    # In your error you had "limit: 0"
    return "limit: 0" in err

def _parse_retry_seconds(err: str, default: float = 2.0) -> float:
    m = re.search(r"retry in\s+([0-9.]+)s", err, re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(r"retry_delay\s*\{\s*seconds:\s*([0-9]+)\s*\}", err)
    if m:
        return float(m.group(1))
    return default

def generate_with_backoff(prompt: str, timeout: int | None = None) -> str:
    """
    Central generation wrapper:
    - tries up to MAX_MODELS_TO_TRY models
    - for 429: waits retry_delay (+ jitter) and retries once (FREE_TIER_MODE)
    - if limit: 0 -> fail fast (no point in retrying/spamming)
    """
    timeout = int(timeout or DEFAULT_TIMEOUT)
    last_err = None

    for model_name in model_candidates():
        model = genai.GenerativeModel(model_name)

        for attempt in range(MAX_RETRIES_429 + 1):
            try:
                resp = model.generate_content(prompt, request_options={"timeout": timeout})
                return resp.text or ""
            except Exception as e:
                err = str(e)
                last_err = err

                if _quota_is_zero(err):
                    raise RuntimeError(
                        f"Quota appears to be 0 for this project/key (model={model_name}). "
                        f"Stop calling API; wait for quota reset or fix project/quota."
                    )

                if _is_429(err) and attempt < MAX_RETRIES_429:
                    wait_s = _parse_retry_seconds(err, default=2.0)
                    time.sleep(wait_s + random.random())  # jitter
                    continue

                # Other error or retries exhausted -> next model
                break

    raise RuntimeError(f"All models failed. Last error: {last_err}")


# ─────────────────────────────────────────────────────────────
# CACHE (DISK)
# ─────────────────────────────────────────────────────────────

def _cache_key(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

def cache_get(prompt: str):
    if not CACHE_DIR:
        return None
    key = _cache_key(prompt)
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

def cache_set(prompt: str, obj):
    if not CACHE_DIR:
        return
    key = _cache_key(prompt)
    path = CACHE_DIR / f"{key}.json"
    try:
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# ROBUST JSON CLEANER
# ─────────────────────────────────────────────────────────────

def clean_ai_json(text: str):
    """
    Extract JSON even if surrounded by text/markdown.
    Returns dict/list or None.
    """
    try:
        if not text:
            return None
        text = re.sub(r"```json\s*|\s*```", "", text).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
        return json.loads(text)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# FEATURE: ANALYZE FILE (JSON OUTPUT)
# ─────────────────────────────────────────────────────────────

def analyze_file(file_path, archive_contents=""):
    file_path = Path(file_path)

    prompt = f"""You are a business analyst evaluating digital assets for online marketplace sales.

Analyze this asset:
- Filename: {file_path.name}
- Type: {file_path.suffix}
- Archive contents (if applicable): {archive_contents if archive_contents else "Single file"}

Return ONLY valid JSON (no markdown fences, no extra text) with:
{{
  "category": "Design Files|3D Models|eBooks|Courses|Templates|Stock Media|Code/Scripts|Other",
  "rating": 1-10,
  "price": "$X",
  "platform": "Etsy|Creative Market|Gumroad|ThemeForest|etc",
  "keywords": "comma,separated,tags",
  "summary": "One-line value proposition"
}}

Constraints for free-tier:
- Keep it short.
- No extra commentary.
"""

    cached = cache_get(prompt)
    if cached:
        return cached

    try:
        text = generate_with_backoff(prompt, timeout=DEFAULT_TIMEOUT)
        data = clean_ai_json(text)
        if isinstance(data, dict) and all(k in data for k in ["category", "rating", "price", "platform", "keywords", "summary"]):
            cache_set(prompt, data)
            return data
    except Exception:
        pass

    return {
        "category": "Other",
        "rating": 5,
        "price": "$10",
        "platform": "Manual",
        "keywords": "digital,asset",
        "summary": "AI analysis unavailable - manual review needed",
    }


# ─────────────────────────────────────────────────────────────
# FEATURE: SEO PACK (TEXT OUTPUT)
# ─────────────────────────────────────────────────────────────

def generate_seo_pack(analysis_result, filename):
    prompt = f"""Create SEO-optimized marketplace listing content for this digital product:

Product: {filename}
Category: {analysis_result.get('category', 'Digital Asset')}
Summary: {analysis_result.get('summary', '')}
Keywords: {analysis_result.get('keywords', '')}

Generate:
1) SEO Title (<= 60 chars)
2) Short Description (<= 160 chars)
3) Full Description (max 2 short paragraphs)
4) 13 Tags (comma-separated)
5) Target Audience (1 sentence)

Constraints for free-tier:
- Be concise.
- No extra headings beyond the 1-5 list.
"""

    cached = cache_get(prompt)
    if cached and isinstance(cached, dict) and "text" in cached:
        return cached["text"]

    try:
        text = generate_with_backoff(prompt, timeout=DEFAULT_TIMEOUT)
        out = (text or "").strip()
        cache_set(prompt, {"text": out})
        return out
    except Exception as e:
        return f"SEO generation failed: {e}\n\nManual SEO needed for: {filename}"


# ─────────────────────────────────────────────────────────────
# FEATURE: BUSINESS CONSULTANT (TASK EXTRACTION)
# ─────────────────────────────────────────────────────────────

def ai_business_consultant(user_message, context=None):
    ctx_json = json.dumps(context, ensure_ascii=False, indent=2) if context else "No extra context."

    prompt = f"""You are an AI Business Consultant helping Shadow and Maria manage their digital asset business.
Current date: {datetime.now().strftime('%Y-%m-%d')}

BUSINESS CONTEXT:
{ctx_json}

USER QUESTION:
{user_message}

Instructions:
- Give practical, revenue-focused advice.
- Keep it concise (free-tier).
- If you suggest tasks, end with:

SUGGESTED TASKS:
- Title: Description
- Title: Description
"""

    cached = cache_get(prompt)
    if cached and isinstance(cached, dict) and "response" in cached:
        return cached

    try:
        text = generate_with_backoff(prompt, timeout=DEFAULT_TIMEOUT * 2)
        full_text = (text or "").strip()

        tasks = []
        if "SUGGESTED TASKS:" in full_text:
            parts = full_text.split("SUGGESTED TASKS:", 1)
            main_body = parts[0].strip()
            task_lines = parts[1].strip().split("\n")
            for line in task_lines:
                line = line.strip()
                if (line.startswith("-") or line.startswith("•")) and ":" in line:
                    t = line[1:].split(":", 1)
                    tasks.append({"title": t[0].strip(), "description": t[1].strip()})
        else:
            main_body = full_text

        result = {"response": main_body, "suggested_tasks": tasks}
        cache_set(prompt, result)
        return result

    except Exception as e:
        return {
            "response": f"AI Consultant unavailable: {e}",
            "suggested_tasks": [],
        }


# ─────────────────────────────────────────────────────────────
# FEATURE: MARKET RESEARCH (TEXT)
# ─────────────────────────────────────────────────────────────

def ai_market_research(product_name, category):
    prompt = f"""As a market research analyst, give realistic pricing insights for:

Product Type: {product_name}
Category: {category}

Return short bullet points:
- Typical price range (Etsy)
- Typical price range (Creative Market/Gumroad)
- Competition intensity (Low/Medium/High)
- Pricing recommendation (1 line)
- Demand (High/Medium/Low)

Constraints: concise, no filler.
"""
    cached = cache_get(prompt)
    if cached and isinstance(cached, dict) and "text" in cached:
        return cached["text"]

    try:
        text = generate_with_backoff(prompt, timeout=DEFAULT_TIMEOUT)
        out = (text or "").strip()
        cache_set(prompt, {"text": out})
        return out
    except Exception as e:
        return f"Market research unavailable: {e}"


# ─────────────────────────────────────────────────────────────
# FEATURE: BUNDLES (TEXT)
# ─────────────────────────────────────────────────────────────

def ai_suggest_bundle(asset_list):
    prompt = f"""Suggest 2-3 profitable bundles from this asset list to increase AOV.

Assets JSON:
{json.dumps(asset_list, ensure_ascii=False)}

Return:
- Bundle name
- Included assets
- Suggested price
- Best platform
- 1-sentence marketing angle

Constraints: concise.
"""
    cached = cache_get(prompt)
    if cached and isinstance(cached, dict) and "text" in cached:
        return cached["text"]

    try:
        text = generate_with_backoff(prompt, timeout=DEFAULT_TIMEOUT)
        out = (text or "").strip()
        cache_set(prompt, {"text": out})
        return out
    except Exception as e:
        return f"Bundle suggestion failed: {e}"


# ─────────────────────────────────────────────────────────────
# FEATURE: CHAT CONTEXT SUMMARY (TEXT)
# ─────────────────────────────────────────────────────────────

def ai_analyze_chat_context(conversation_history):
    if not conversation_history:
        return ""

    recent = conversation_history[-5:]
    prompt = f"""Summarize key topics and decisions from this conversation (2-3 sentences max):

{json.dumps(recent, ensure_ascii=False, indent=2)}
"""
    cached = cache_get(prompt)
    if cached and isinstance(cached, dict) and "text" in cached:
        return cached["text"]

    try:
        text = generate_with_backoff(prompt, timeout=10)
        out = (text or "").strip()
        cache_set(prompt, {"text": out})
        return out
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────
# FEATURE: WEEKLY REPORT (TEXT)  ✅ FIXED (in your code it was incomplete)
# ─────────────────────────────────────────────────────────────

def ai_weekly_report(stats):
    prompt = f"""Generate a weekly business performance report based on these stats:

{json.dumps(stats, ensure_ascii=False, indent=2)}

Return:
1) Highlights (3 bullets)
2) Metrics summary (short)
3) What to improve next week (3 bullets)
4) 1 opportunity to test

Constraints: concise.
"""
    cached = cache_get(prompt)
    if cached and isinstance(cached, dict) and "text" in cached:
        return cached["text"]

    try:
        text = generate_with_backoff(prompt, timeout=DEFAULT_TIMEOUT)
        out = (text or "").strip()
        cache_set(prompt, {"text": out})
        return out
    except Exception as e:
        return f"Report failed: {e}"


# ─────────────────────────────────────────────────────────────
# FEATURE: BUSINESS IDEA EVALUATION (JSON)
# ─────────────────────────────────────────────────────────────

def evaluate_business_idea(idea: dict, context: dict = None) -> dict:
    context_info = ""
    if context:
        context_info = f"\n\nExtra Context:\n{json.dumps(context, ensure_ascii=False, indent=2)}"

    prompt = f"""You are a strict business analyst and SaaS investor.
Return ONLY valid JSON (no markdown, no extra text).

Idea:
{json.dumps(idea, ensure_ascii=False, indent=2)}
{context_info}

Schema:
{{
  "market": {{"tam_usd": number, "sam_usd": number, "som_usd": number, "notes": string}},
  "customer": {{"icp": string, "pain_level_1_10": number}},
  "monetization": {{"model": "subscription|usage|hybrid|one_time", "pricing_monthly_usd_low": number, "pricing_monthly_usd_high": number}},
  "execution": {{"time_to_mvp_weeks": number, "key_risks": [string]}},
  "investor_view": {{"verdict": "go|iterate|no_go", "verdict_reason": string}}
}}

Constraints: be concise.
"""
    cached = cache_get(prompt)
    if cached and isinstance(cached, dict) and "evaluation" in cached:
        return cached

    try:
        text = generate_with_backoff(prompt, timeout=DEFAULT_TIMEOUT)
        data = clean_ai_json(text)
        if data:
            result = {"evaluation": data, "model_used": model_candidates()[0]}
            cache_set(prompt, result)
            return result
    except Exception as e:
        return {"evaluation": {"error": f"AI evaluation failed: {e}"}, "model_used": None}

    return {"evaluation": {"error": "AI evaluation failed: invalid JSON"}, "model_used": None}


# ─────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────

def engine_status():
    return {
        "status": "online",
        "free_tier_mode": FREE_TIER_MODE,
        "models_configured": model_candidates(),
        "timestamp": datetime.now().isoformat(),
        "cache_dir": str(CACHE_DIR) if CACHE_DIR else None,
    }
