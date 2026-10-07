"""Assemble what the Cloudflare site serves: public/ = web/static/ plus
showcase/, and src/limits.json from config.py, so the upload limits are set
in one place. wrangler runs this before every deploy and dev session.

Usage (from deploy/cloudflare/, or let wrangler run it):
    python build_site.py
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    DAILY_JOB_LIMIT,
    DAILY_JOBS_PER_VISITOR,
    JOB_KEEP_SECONDS,
    MAX_QUEUED_JOBS,
    MAX_UPLOAD_MB,
    MAX_UPLOAD_PAGES,
    SHOWCASE_DIR,
)

PUBLIC = HERE / "public"


def main():
    shutil.rmtree(PUBLIC, ignore_errors=True)
    shutil.copytree(PROJECT_ROOT / "web" / "static", PUBLIC)
    shutil.copytree(SHOWCASE_DIR, PUBLIC / "showcase")

    limits = {
        "pages": MAX_UPLOAD_PAGES,
        "mb": MAX_UPLOAD_MB,
        "queued": MAX_QUEUED_JOBS,
        "daily": DAILY_JOB_LIMIT,
        "per_visitor": DAILY_JOBS_PER_VISITOR,
        "keep_seconds": JOB_KEEP_SECONDS,
    }
    (HERE / "src" / "limits.json").write_text(json.dumps(limits, indent=2) + "\n", encoding="utf-8")

    files = [f for f in PUBLIC.rglob("*") if f.is_file()]
    print(f"public/: {len(files)} files, {sum(f.stat().st_size for f in files) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
