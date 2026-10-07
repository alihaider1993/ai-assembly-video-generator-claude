"""This PC as the render machine for the Cloudflare site (deploy/cloudflare/).
While it runs, the site shows "Render machine online" and takes uploads; it
fetches each one, makes the video with web/pipeline_job.py (Gemini reads
the manual, the pipeline renders it with Blender here) and sends the video
back. Nothing about the pipeline leaves this machine but the finished video.

Usage (from the repo root; SITE_URL, WORKER_SECRET and GEMINI_API_KEY in .env):
    python web/worker.py

Stop it with Ctrl+C; the site then shows uploads as closed within a minute.
It takes no job while another pipeline run is going on this machine (output
paths are fixed), and keeps each job's log in outputs/jobs/<id>/log.txt.
"""
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from config import JOBS_DIR
from web.pipeline_job import FAILED_BUILDING, run_job

POLL_SECONDS = 5
HEARTBEAT_SECONDS = 30
KEEP_LOCAL_LOGS = 20


class Site:
    def __init__(self, url: str, secret: str):
        self.url = url.rstrip("/")
        self.secret = secret

    def call(self, method: str, path: str, body: bytes = None, headers: dict = None):
        """(status, body bytes) for /api/worker/<path>."""
        request = urllib.request.Request(
            f"{self.url}/api/worker/{path}", data=body, method=method,
            headers={"authorization": f"Bearer {self.secret}", "user-agent": "render-machine", **(headers or {})},
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def post_json(self, path: str, data: dict):
        return self.call("POST", path, json.dumps(data).encode(), {"content-type": "application/json"})


def other_pipeline_running() -> bool:
    """Whether a pipeline run someone started by hand is going on here."""
    try:
        if os.name == "nt":
            # The pattern's "\." keeps this PowerShell command from matching itself.
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'run_mvp_pipeline\\.py' } "
                 "| Measure-Object | Select-Object -ExpandProperty Count"],
                capture_output=True, text=True, timeout=30,
            ).stdout.strip()
            return int(out or 0) > 0
        out = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True, timeout=30).stdout
        return "run_mvp_pipeline" in out
    except (OSError, ValueError, subprocess.SubprocessError):
        return False


def keep_alive(site: Site, stop: threading.Event):
    while not stop.wait(HEARTBEAT_SECONDS):
        try:
            site.call("POST", "heartbeat")
        except OSError:
            pass


def process(site: Site, job_id: str):
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    status, pdf = site.call("GET", f"jobs/{job_id}/pdf")
    if status != 200:
        print(f"[{job_id}] couldn't fetch the PDF ({status})")
        return
    (job_dir / "manual.pdf").write_bytes(pdf)
    print(f"[{job_id}] started ({len(pdf) / 1e6:.1f} MB PDF)")

    stop = threading.Event()
    threading.Thread(target=keep_alive, args=(site, stop), daemon=True).start()
    started = time.time()
    try:
        with open(job_dir / "log.txt", "w", encoding="utf-8") as log:
            ok, text = run_job(
                job_dir / "manual.pdf", f"upload_{job_id}", job_dir / "video.mp4", log,
                lambda phase: site.post_json(f"jobs/{job_id}/phase", {"phase": phase}),
            )
    except Exception as e:  # report and keep serving
        ok, text = False, FAILED_BUILDING
        print(f"[{job_id}] error: {e!r}")
    finally:
        stop.set()

    if ok:
        video = (job_dir / "video.mp4").read_bytes()
        status, _ = site.call("POST", f"jobs/{job_id}/done", video,
                              {"content-type": "video/mp4", "x-title": urllib.parse.quote(text)})
        print(f"[{job_id}] done: {text} ({time.time() - started:.0f} s, upload {status})")
    else:
        site.post_json(f"jobs/{job_id}/failed", {"message": text})
        print(f"[{job_id}] failed: {text} (log: {job_dir / 'log.txt'})")
    (job_dir / "manual.pdf").unlink(missing_ok=True)
    (job_dir / "video.mp4").unlink(missing_ok=True)


def prune_logs():
    """Keep the logs of the last KEEP_LOCAL_LOGS jobs."""
    if JOBS_DIR.exists():
        for old in sorted(JOBS_DIR.iterdir(), key=lambda d: d.stat().st_mtime)[:-KEEP_LOCAL_LOGS]:
            shutil.rmtree(old, ignore_errors=True)


def main():
    load_dotenv(PROJECT_ROOT / ".env")
    url, secret = os.environ.get("SITE_URL", ""), os.environ.get("WORKER_SECRET", "")
    if not url or not secret:
        sys.exit("Set SITE_URL and WORKER_SECRET in .env first.")
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("Set GEMINI_API_KEY in .env first: Gemini reads the uploaded manuals.")

    site = Site(url, secret)
    print(f"Render machine for {site.url}: online. Ctrl+C to stop.")
    busy_noted = False
    while True:
        try:
            if other_pipeline_running():
                if not busy_noted:
                    print("Another pipeline run is going on here; waiting for it to finish.")
                    busy_noted = True
                site.call("POST", "heartbeat")
            else:
                busy_noted = False
                status, body = site.call("POST", "poll")
                if status == 200:
                    process(site, json.loads(body)["id"])
                    prune_logs()
                    continue
                if status not in (204,):
                    print(f"The site answered {status}; check SITE_URL and WORKER_SECRET.")
        except OSError as e:
            print(f"Can't reach the site ({e}); retrying.")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRender machine stopped; the site will show uploads as closed within a minute.")
