"""The public website: the showcase (finished videos picked with
utils/showcase.py) and "try your own manual" uploads.

Usage (from the repo root):
    uvicorn web.server:app --port 7860

Uploads are checked (PDF, MAX_UPLOAD_PAGES pages, MAX_UPLOAD_MB), queued and
run one at a time (web/pipeline_job.py), because the pipeline's output paths
are fixed; the video is kept for JOB_KEEP_SECONDS. This is the self-hosted
version (Dockerfile); the free deployment is deploy/cloudflare/ with
web/worker.py rendering on this PC.

The site is public and the pipeline is not: browsers only ever get the
showcase files, a job's state, a plain-language phase and a generic error.
Stage names, logs and intermediate files stay on the server (each job's
log is outputs/jobs/<id>/log.txt). The API docs are switched off.
"""
import queue
import shutil
import sys
import threading
import time
import uuid
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import (
    DAILY_JOB_LIMIT,
    DAILY_JOBS_PER_VISITOR,
    JOB_KEEP_SECONDS,
    JOBS_DIR,
    MAX_QUEUED_JOBS,
    MAX_UPLOAD_MB,
    MAX_UPLOAD_PAGES,
    SHOWCASE_DIR,
)
from utils.pdf_to_images import upload_problem
from web.pipeline_job import FAILED_BUILDING, PHASES, run_job

STATIC_DIR = Path(__file__).resolve().parent / "static"

class Jobs:
    """Uploads waiting, running and done, with the daily caps. One worker
    thread runs them in order."""

    def __init__(self):
        self.lock = threading.Lock()
        self.jobs = {}
        self.waiting = queue.Queue()
        self.day = date.today()
        self.today_total = 0
        self.today_by_visitor = {}

    def limit_problem(self, visitor: str) -> str:
        if date.today() != self.day:
            self.day, self.today_total, self.today_by_visitor = date.today(), 0, {}
        if sum(j["state"] == "queued" for j in self.jobs.values()) >= MAX_QUEUED_JOBS:
            return "The queue is full right now. Try again in a few minutes."
        if self.today_total >= DAILY_JOB_LIMIT:
            return "Today's free videos have all been made. Come back tomorrow, or watch the examples above."
        if self.today_by_visitor.get(visitor, 0) >= DAILY_JOBS_PER_VISITOR:
            return f"You can make {DAILY_JOBS_PER_VISITOR} videos a day. Come back tomorrow."
        return ""

    def add(self, visitor: str, pdf_bytes: bytes) -> dict:
        with self.lock:
            problem = self.limit_problem(visitor)
            if problem:
                raise HTTPException(429, problem)
            job_id = uuid.uuid4().hex[:12]
            job_dir = JOBS_DIR / job_id
            job_dir.mkdir(parents=True)
            (job_dir / "manual.pdf").write_bytes(pdf_bytes)
            self.jobs[job_id] = {"state": "queued", "phase": 0, "title": "", "message": "", "finished": None}
            self.today_total += 1
            self.today_by_visitor[visitor] = self.today_by_visitor.get(visitor, 0) + 1
        self.waiting.put(job_id)
        return self.status(job_id)

    def status(self, job_id: str) -> dict:
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                raise HTTPException(404, "This video has expired. Upload the manual again.")
            # Jobs are kept in the order they arrived.
            ahead = 0
            if job["state"] == "queued":
                for other_id, other in self.jobs.items():
                    if other_id == job_id:
                        break
                    ahead += other["state"] in ("queued", "running")
            return {
                "id": job_id,
                "state": job["state"],
                "position": ahead,
                "phase": job["phase"],
                "phases": PHASES,
                "title": job["title"],
                "message": job["message"],
            }

    def update(self, job_id: str, **fields):
        with self.lock:
            self.jobs[job_id].update(fields)

    def clean_up(self):
        """Forget finished jobs older than JOB_KEEP_SECONDS and delete their files."""
        with self.lock:
            old = [
                job_id for job_id, job in self.jobs.items()
                if job["finished"] and time.time() - job["finished"] > JOB_KEEP_SECONDS
            ]
            for job_id in old:
                del self.jobs[job_id]
        for job_id in old:
            shutil.rmtree(JOBS_DIR / job_id, ignore_errors=True)

    def work(self):
        while True:
            job_id = self.waiting.get()
            try:
                self.run(job_id)
            except Exception as e:  # keep the worker alive whatever happens
                with open(JOBS_DIR / job_id / "log.txt", "a", encoding="utf-8") as log:
                    log.write(f"\n[WORKER ERROR] {e!r}\n")
                self.update(job_id, state="failed", message=FAILED_BUILDING, finished=time.time())
            self.clean_up()

    def run(self, job_id: str):
        job_dir = JOBS_DIR / job_id
        self.update(job_id, state="running")
        with open(job_dir / "log.txt", "w", encoding="utf-8") as log:
            ok, text = run_job(
                job_dir / "manual.pdf", f"upload_{job_id}", job_dir / "video.mp4", log,
                lambda phase: self.update(job_id, phase=phase),
            )
        if ok:
            self.update(job_id, state="done", phase=len(PHASES) - 1, title=text, finished=time.time())
        else:
            self.update(job_id, state="failed", message=text, finished=time.time())


def visitor_of(request: Request) -> str:
    # Behind Hugging Face's proxy the visitor's address is the first
    # X-Forwarded-For entry.
    forwarded = request.headers.get("x-forwarded-for", "")
    return forwarded.split(",")[0].strip() or (request.client.host if request.client else "unknown")


jobs = Jobs()


@asynccontextmanager
async def lifespan(app: FastAPI):
    shutil.rmtree(JOBS_DIR, ignore_errors=True)
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    threading.Thread(target=jobs.work, daemon=True).start()
    yield


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)


@app.get("/api/limits")
def limits():
    # This server renders uploads itself, so it is always "online".
    return {"pages": MAX_UPLOAD_PAGES, "mb": MAX_UPLOAD_MB, "online": True}


@app.post("/api/jobs")
async def create_job(request: Request, file: UploadFile = File(...)):
    data = await file.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
    problem = upload_problem(data)
    if problem:
        raise HTTPException(400, problem)
    return jobs.add(visitor_of(request), data)


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    return jobs.status(job_id)


@app.get("/api/jobs/{job_id}/video")
def job_video(job_id: str):
    if jobs.status(job_id)["state"] != "done":
        raise HTTPException(404, "The video isn't ready yet.")
    title = jobs.status(job_id)["title"] or "assembly"
    return FileResponse(
        JOBS_DIR / job_id / "video.mp4", media_type="video/mp4",
        filename=f"{title.lower().replace(' ', '_')}_assembly.mp4", content_disposition_type="inline",
    )


@app.exception_handler(Exception)
async def hide_errors(request: Request, exc: Exception):
    # Never send a traceback to the browser.
    return JSONResponse({"detail": "Something went wrong."}, status_code=500)


app.mount("/showcase", StaticFiles(directory=SHOWCASE_DIR), name="showcase")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="site")
