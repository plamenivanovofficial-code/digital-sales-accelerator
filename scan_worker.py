"""
OMEGA v4 TITANIUM - BACKGROUND SCAN WORKER
Runs long scans without blocking Streamlit UI.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import sqlite3

import config
import database
import scanner
import ai_engine


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-id", type=int, required=True)
    ap.add_argument("--sleep-per-ai", type=float, default=4.5)
    ap.add_argument("--batch-size", type=int, default=20)
    return ap.parse_args()


def _looks_like_429(err: Exception) -> bool:
    s = str(err)
    return ("429" in s) or ("quota" in s.lower()) or ("rate" in s.lower() and "limit" in s.lower())


def main():
    args = parse_args()

    conn = database.init_db(config.DATABASE_PATH)
    job = database.get_scan_job(conn, args.job_id)
    if not job:
        print(f"Job not found: {args.job_id}", file=sys.stderr)
        return 2

    zone = job.get("zone") or "Unknown"
    base_path = Path(job.get("base_path") or ".")
    file_types_json = job.get("file_types_json")
    file_types = None
    if file_types_json:
        try:
            file_types = json.loads(file_types_json)
            if file_types is not None:
                file_types = set(file_types)
        except Exception:
            file_types = None

    # Create unique session ID for this scan
    session_id = f"scan_{args.job_id}_{int(time.time())}"

    # Mark running
    database.set_scan_job_status(conn, args.job_id, "running")

    # Pre-count candidates for progress %
    total_candidates = 0
    try:
        for _ in scanner.iter_scan_files(base_path, base_path, file_types=file_types):
            total_candidates += 1
        database.update_scan_job_progress(conn, args.job_id, total_candidates=total_candidates)
    except Exception as e:
        database.set_scan_job_status(conn, args.job_id, "error", last_error=str(e))
        return 3

    processed = 0
    skipped = 0
    errors = 0
    seen = 0

    batch = []

    def flush_batch(batch_items):
        nonlocal processed, skipped, errors
        for (bf, bh) in batch_items:
            # stop requested?
            job_now = database.get_scan_job(conn, args.job_id)
            if job_now and int(job_now.get("stop_requested") or 0) == 1:
                database.set_scan_job_status(conn, args.job_id, "stopped")
                return False

            database.update_scan_job_progress(conn, args.job_id, current_file=str(bf))

            contents = ""
            try:
                if bf.suffix.lower() in config.ARCHIVE_EXTENSIONS:
                    contents = scanner.get_archive_contents(bf)
            except Exception:
                contents = ""

            # AI analyze with basic backoff for 429
            attempt = 0
            while True:
                try:
                    analysis = ai_engine.analyze_file(bf, contents)
                    database.save_asset(conn, bf, analysis, bh, user=job.get("created_by") or "System")
                    processed += 1
                    database.update_scan_job_progress(conn, args.job_id, processed=processed)
                    
                    # Log successful addition
                    database.log_scan_file(
                        conn, session_id, zone, str(bf), bf.name, bh,
                        action='added', status='success'
                    )
                    break
                except Exception as e:
                    attempt += 1
                    errors += 1
                    database.update_scan_job_progress(conn, args.job_id, errors=errors, last_error=str(e))
                    
                    # Log error
                    database.log_scan_file(
                        conn, session_id, zone, str(bf), bf.name, bh,
                        action='error', status='error', error_msg=str(e)
                    )

                    if _looks_like_429(e) and attempt <= 6:
                        # exponential backoff: 5, 10, 20, 40, 60...
                        sleep_s = min(60.0, 5.0 * (2 ** (attempt - 1)))
                        time.sleep(sleep_s)
                        continue
                    # non-retryable
                    break

            time.sleep(args.sleep_per_ai)

        return True

    try:
        for file in scanner.iter_scan_files(base_path, base_path, file_types=file_types):
            # stop requested?
            job_now = database.get_scan_job(conn, args.job_id)
            if job_now and int(job_now.get("stop_requested") or 0) == 1:
                database.set_scan_job_status(conn, args.job_id, "stopped")
                return 0

            seen += 1
            database.update_scan_job_progress(conn, args.job_id, seen_files=seen, current_file=str(file))

            # Compute hash/fingerprint
            f_hash = scanner.get_file_hash(file, warn=False)
            if not f_hash:
                skipped += 1
                database.update_scan_job_progress(conn, args.job_id, skipped=skipped)
                continue

            # Skip already scanned
            if database.is_duplicate(conn, f_hash):
                skipped += 1
                database.update_scan_job_progress(conn, args.job_id, skipped=skipped)
                
                # Log skipped duplicate
                database.log_scan_file(
                    conn, session_id, zone, str(file), file.name, f_hash,
                    action='skipped_duplicate', status='skipped'
                )
                continue

            batch.append((file, f_hash))

            if len(batch) >= args.batch_size:
                ok = flush_batch(batch)
                batch = []
                if not ok:
                    return 0

        if batch:
            ok = flush_batch(batch)
            if not ok:
                return 0

        database.set_scan_job_status(conn, args.job_id, "completed")
        database.update_scan_job_progress(conn, args.job_id, current_file=None)

    except Exception as e:
        database.set_scan_job_status(conn, args.job_id, "error", last_error=str(e))
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
