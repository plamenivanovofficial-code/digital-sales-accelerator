"""
OMEGA v4 TITANIUM - SCANNER MODULE
Multi-drive file scanner with AI analysis integration
"""

import hashlib
import zipfile
import rarfile
from pathlib import Path

try:
    import streamlit as st
except Exception:  # pragma: no cover

    class _DummySt:
        def __getattr__(self, name):
            def _noop(*args, **kwargs):
                return None

            return _noop

    st = _DummySt()

import config
import security


def get_file_hash(file_path, algorithm="sha256", warn=True):
    """
    Calculate a stable identifier for duplicate detection.

    - For normal-sized files: full-file hash (SHA-256 default).
    - For very large files (> config.MAX_HASH_SIZE): returns a *fingerprint* hash
      based on size + first/last chunks. This avoids skipping large ZIP/RAR files.
    """
    try:
        p = Path(file_path)
        file_size = p.stat().st_size

        # Large file → fingerprint (size + first/last chunks)
        if file_size > config.MAX_HASH_SIZE:
            # Avoid spamming the UI with warnings on every file
            if warn:
                try:
                    key = "warned_large_hash"
                    warned = getattr(st.session_state, key, False)
                    if not warned:
                        st.session_state[key] = True
                        st.info(
                            "ℹ️ Large files detected: using fingerprint hashing (fast/partial) instead of full hashing."
                        )
                except Exception:
                    pass

            hasher = hashlib.sha256()
            hasher.update(str(file_size).encode("utf-8"))

            chunk = 2 * 1024 * 1024  # 2MB head/tail
            with open(p, "rb") as f:
                head = f.read(chunk)
                hasher.update(head)

                if file_size > chunk:
                    try:
                        f.seek(max(0, file_size - chunk))
                        tail = f.read(chunk)
                        hasher.update(tail)
                    except Exception:
                        # If tail read fails for any reason, head+size is still usable
                        pass

            return "FP_SHA256_" + hasher.hexdigest()

        # Normal file → full hash
        hasher = hashlib.sha256() if algorithm == "sha256" else hashlib.md5()

        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    except PermissionError:
        try:
            st.error(f"⛔ Permission denied: {Path(file_path).name}")
        except Exception:
            pass
        return None
    except Exception as e:
        try:
            st.warning(f"⚠️ Error hashing file: {e}")
        except Exception:
            pass
        return None


def get_archive_contents(archive_path):
    """
    Extract file list from ZIP/RAR/7z archives.
    Returns preview of contents for AI analysis.
    """
    try:
        archive_path = Path(archive_path)
        suffix = archive_path.suffix.lower()

        if suffix == ".zip":
            with zipfile.ZipFile(archive_path, "r") as z:
                files = z.namelist()
                preview = ", ".join([f.split("/")[-1] for f in files[:20]])
                return f"{len(files)} files: {preview}"

        elif suffix == ".rar":
            with rarfile.RarFile(archive_path, "r") as r:
                files = r.namelist()
                preview = ", ".join([f.split("/")[-1] for f in files[:20]])
                return f"{len(files)} files: {preview}"

        elif suffix == ".7z":
            try:
                import py7zr

                with py7zr.SevenZipFile(archive_path, "r") as z:
                    files = z.getnames()
                    preview = ", ".join([f.split("/")[-1] for f in files[:20]])
                    return f"{len(files)} files: {preview}"
            except ImportError:
                return "7z archive (install py7zr to inspect)"

    except Exception as e:
        return f"Archive (error reading: {str(e)[:50]})"

    return "Archive file"


def is_allowed_file(file_path):
    """
    Check if file extension is allowed
    Returns: (is_allowed, reason)
    """
    ext = Path(file_path).suffix.lower()

    # Check blocked first (security priority)
    if ext in config.BLOCKED_EXTENSIONS:
        return False, f"Blocked file type: {ext}"

    # Check allowed
    if ext in config.ALLOWED_EXTENSIONS or ext == "":
        return True, ""

    # Unknown extension - warn but allow
    return True, f"Unknown file type: {ext}"


def get_items_in_path(current_path, base_dir, show_hidden=False):
    """
    Get items in directory with security checks
    Returns: list of Path objects (sorted)
    """
    try:
        p = Path(current_path)

        # CRITICAL: Path traversal protection
        if not security.is_safe_path(p, base_dir):
            st.error("⛔ SECURITY: Path traversal attempt detected!")
            return []

        # Validate path is safe to access
        is_valid, error_msg = security.validate_scan_path(p)
        if not is_valid:
            st.error(error_msg)
            return []

        if not p.is_dir():
            st.error(f"⚠️ Not a directory: {p}")
            return []

        # List items with filtering
        items = []
        for item in p.iterdir():
            # Skip hidden files unless requested
            if not show_hidden and item.name.startswith("."):
                continue

            # For files, check extension
            if item.is_file():
                is_allowed, reason = is_allowed_file(item)
                if is_allowed:
                    items.append(item)
                elif reason.startswith("Blocked"):
                    st.warning(f"⛔ {reason}: {item.name}")
            else:
                # Always allow directories
                items.append(item)

        # Sort: directories first, then by name
        return sorted(items, key=lambda x: (not x.is_dir(), x.name.lower()))

    except PermissionError:
        st.error(f"⛔ Permission denied: {current_path}")
        return []
    except Exception as e:
        st.error(f"⚠️ Error reading directory: {e}")
        return []


def scan_directory_recursive(directory_path, base_dir, file_types=None, max_files=100):
    """
    Recursively scan directory for specific file types
    Used by the main Scanner module

    Args:
        directory_path: Directory to scan
        base_dir: Base directory for security checks
        file_types: Set of extensions to look for (e.g., {'.zip', '.psd'})
        max_files: Maximum files to return (prevent overwhelming)

    Returns:
        List of Path objects matching criteria
    """
    found_files = []

    try:
        # Validate path
        is_valid, error_msg = security.validate_scan_path(directory_path)
        if not is_valid:
            st.error(error_msg)
            return []

        p = Path(directory_path)

        # Use rglob for recursive search
        if file_types:
            for ext in file_types:
                pattern = f"**/*{ext}"
                for file in p.rglob(pattern):
                    # Security check each file
                    if not security.is_safe_path(file, base_dir):
                        continue

                    # Skip blacklisted paths
                    skip = False
                    for blacklisted in config.BLACKLIST_PATHS:
                        if blacklisted in str(file).upper():
                            skip = True
                            break

                    if not skip:
                        found_files.append(file)

                        if len(found_files) >= max_files:
                            st.warning(
                                f"⚠️ Reached limit of {max_files} files. Stopping scan."
                            )
                            return found_files
        else:
            # Scan all allowed file types
            for file in p.rglob("*"):
                if file.is_file():
                    is_allowed, _ = is_allowed_file(file)
                    if is_allowed and security.is_safe_path(file, base_dir):
                        # Skip blacklisted paths
                        skip = False
                        for blacklisted in config.BLACKLIST_PATHS:
                            if blacklisted in str(file).upper():
                                skip = True
                                break

                        if not skip:
                            found_files.append(file)

                            if len(found_files) >= max_files:
                                st.warning(f"⚠️ Reached limit of {max_files} files.")
                                return found_files

        return found_files

    except PermissionError:
        st.error(f"⛔ Permission denied: {directory_path}")
        return []
    except Exception as e:
        st.error(f"⚠️ Scan error: {e}")
        return []


def get_file_info(file_path):
    """
    Get comprehensive file information
    Returns: dict with file metadata
    """
    try:
        p = Path(file_path)
        stat = p.stat()

        info = {
            "name": p.name,
            "path": str(p),
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "extension": p.suffix.lower(),
            "is_dir": p.is_dir(),
            "is_archive": p.suffix.lower() in config.ARCHIVE_EXTENSIONS,
            "is_image": p.suffix.lower() in config.IMAGE_EXTENSIONS,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

        # If archive, get contents preview
        if info["is_archive"]:
            info["archive_contents"] = get_archive_contents(p)

        return info

    except Exception as e:
        return {"error": str(e)}


def get_scan_statistics(directory_path, base_dir):
    """
    Get directory statistics for overview
    Returns: dict with counts and totals
    """
    try:
        is_valid, error_msg = security.validate_scan_path(directory_path)
        if not is_valid:
            return {"error": error_msg}

        p = Path(directory_path)

        stats = {
            "total_files": 0,
            "total_dirs": 0,
            "total_size": 0,
            "file_types": {},
            "categories": {cat: 0 for cat in config.ASSET_CATEGORIES},
        }

        for item in p.rglob("*"):
            if not security.is_safe_path(item, base_dir):
                continue

            # Skip blacklisted
            skip = False
            for blacklisted in config.BLACKLIST_PATHS:
                if blacklisted in str(item).upper():
                    skip = True
                    break

            if skip:
                continue

            if item.is_file():
                stats["total_files"] += 1
                stats["total_size"] += item.stat().st_size

                ext = item.suffix.lower()
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1

            elif item.is_dir():
                stats["total_dirs"] += 1

        stats["total_size_mb"] = round(stats["total_size"] / (1024 * 1024), 2)
        stats["total_size_gb"] = round(stats["total_size"] / (1024 * 1024 * 1024), 2)

        return stats

    except Exception as e:
        return {"error": str(e)}


# Import datetime for file info
from datetime import datetime


def iter_scan_files(directory_path, base_dir, file_types=None):
    """
    Generator: yields Path objects for matching files (no max limit).
    Respects security + blacklist + allowed extensions.
    """
    p = Path(directory_path)

    is_valid, error_msg = security.validate_scan_path(p)
    if not is_valid:
        st.error(error_msg)
        return

    for file in p.rglob("*"):
        if not file.is_file():
            continue

        if not security.is_safe_path(file, base_dir):
            continue

        # Blacklist check (case-insensitive)
        file_up = str(file).upper()
        if any(str(b).upper() in file_up for b in config.BLACKLIST_PATHS):
            continue

        if file_types:
            if file.suffix.lower() not in file_types:
                continue
        else:
            # respect allowed + blocked rules
            is_allowed, _ = is_allowed_file(file)
            if not is_allowed:
                continue

        yield file
