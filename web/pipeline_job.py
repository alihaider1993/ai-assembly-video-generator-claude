"""Turn one uploaded manual into a video: Gemini reads it, then the pipeline
builds and renders it. Shared by web/server.py (the self-hosted site) and
web/worker.py (this PC as the render machine behind the Cloudflare site).

Visitors only ever see PHASES and the FAILED_* messages; stage names and
logs stay on this machine.
"""
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, TextIO, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import MANUALS_DIR, VIDEOS_DIR, product_title
from utils.pdf_to_images import upload_problem

# What a visitor sees while their manual is processed, and the words in the
# pipeline's "RUNNING: ..." lines that start each phase (checked from the
# last phase back).
PHASES = ["Reading the manual", "Planning the assembly", "Animating in 3D", "Making the video"]
PHASE_STARTS = {3: ("render_video",), 2: ("blender_builder", "blender.exe", "--background")}

FAILED_READING = "We couldn't read this file as a furniture assembly manual. Try another one."
FAILED_BUILDING = "Something went wrong while building the video. Try another manual."


def job_commands(pdf: Path, name: str) -> list:
    """The commands that turn an uploaded PDF into outputs/videos/<name>.mp4."""
    python = sys.executable
    return [
        [python, "-u", "v2/agents/gemini_describer.py", str(pdf), "--name", name],
        [python, "-u", "v2/run_mvp_pipeline.py", name, "--quiet"],
    ]


def run_job(pdf: Path, name: str, video_out: Path, log: TextIO,
            on_phase: Callable[[int], None]) -> Tuple[bool, str]:
    """Make the video for pdf into video_out, as manual `name` (a scratch
    folder under manuals/, removed afterwards). Calls on_phase(i) as each
    of PHASES starts. Returns (True, product title) or (False, the message
    for the visitor)."""
    problem = upload_problem(pdf.read_bytes())
    if problem:
        return False, problem

    try:
        on_phase(0)
        for i, command in enumerate(job_commands(pdf, name)):
            if i == 1:
                on_phase(1)
            process = subprocess.Popen(
                command, cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
            )
            for line in process.stdout:
                log.write(line)
                if line.startswith("RUNNING:"):
                    for phase in sorted(PHASE_STARTS, reverse=True):
                        if any(word in line for word in PHASE_STARTS[phase]):
                            on_phase(phase)
                            break
            if process.wait() != 0:
                return False, FAILED_READING if i == 0 else FAILED_BUILDING

        video = VIDEOS_DIR / f"{name}.mp4"
        if not video.exists():
            return False, FAILED_BUILDING
        video_out.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(video), video_out)
        return True, product_title(MANUALS_DIR / name)
    finally:
        shutil.rmtree(MANUALS_DIR / name, ignore_errors=True)
