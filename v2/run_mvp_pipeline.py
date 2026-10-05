"""Run the whole pipeline for one manual: its vision results -> JSON stages ->
Blender -> MP4.

Usage (from the repo root):
    python v2/run_mvp_pipeline.py NAME       # manuals/NAME/
    python v2/run_mvp_pipeline.py DIR        # any folder with the two vision files
    python v2/run_mvp_pipeline.py NAME --quiet
    python v2/run_mvp_pipeline.py NAME --no-render

--no-render runs every stage up to writing the Blender script, without
Blender or the video (what CI runs).

--quiet prints everything except Blender's per-frame "Saved:" lines and
progress bars, which are only counted; outputs/logs/pipeline.log keeps every
line.

The pipeline starts from the manual's page_states.json and
diagram_analysis.json (written by manuals/NAME/describe.py). The video is
written to outputs/assembly_animation_v3.mp4 and kept as
outputs/videos/NAME.mp4.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, TextIO, Union

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    product_title,
    FRAMES_V3_DIR,
    OUTPUTS_DIR,
    VIDEO_V3_PATH,
    VIDEOS_DIR,
    BLENDER_V3_SCRIPT,
    V2_JSON_DIR,
    V2_OUTPUT_DIR,
    PAGE_STATES_JSON,
    DIAGRAM_ANALYSIS_JSON,
    DIAGRAM_ANALYSIS_COPY_JSON,
    SCENE_LAYOUT_JSON,
    SCENE_LAYOUT_COPY_JSON,
    MANUALS_DIR,
    VISION_FILES,
    is_described,
    ensure_project_dirs,
)

load_dotenv(PROJECT_ROOT / ".env")

BLENDER_EXE = os.environ.get(
    "BLENDER_EXE",
    r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
)

LOG_PATH = OUTPUTS_DIR / "logs" / "pipeline.log"

# Lines --quiet keeps out of the console: one per rendered frame, and the
# progress bars moviepy redraws many times a second.
FRAME_SAVED = re.compile(r"Saved: .*frame_\d+\.png")
PROGRESS_BAR = re.compile(r"\d+%\|")


class CopyStep:
    """In-process file copy, so the pipeline does not need PowerShell."""

    def __init__(self, source: Path, destination: Path):
        self.source = source
        self.destination = destination

    def __str__(self) -> str:
        return f"copy {self.source} -> {self.destination}"


Step = Union[List[str], CopyStep]


def build_steps(fixture_dir: Path, render: bool = True) -> List[Step]:
    steps = [
        CopyStep(fixture_dir / "page_states.json", PAGE_STATES_JSON),
        [sys.executable, "v2/rendering/state_difference_engine.py"],
        [sys.executable, "v2/rendering/assembly_action_extractor.py"],

        # --- PASS 1: initial graph from raw page/action data. ---
        [sys.executable, "v2/rendering/universal_graph_engine.py"],

        [sys.executable, "v2/agents/object_identity_tracker.py"],

        [sys.executable, "v2/rendering/canonical_resolver.py"],

        # Expand resolved actions across sibling instances (4 rails, 2 legs,
        # 2 seat pads, 2 backs) BEFORE the graph is rebuilt, so the graph's
        # connections — and everything downstream of it, including
        # motion_planner.py — actually reflect the full part count instead
        # of just one representative instance per part.
        [sys.executable, "v2/rendering/action_replicator.py"],

        # --- PASS 2: rebuild the graph now using the REPLICATED actions. ---
        [sys.executable, "v2/rendering/universal_graph_engine.py"],

        [sys.executable, "v2/rendering/motion_planner.py"],

        [sys.executable, "v2/rendering/geometry_synthesizer.py"],

        CopyStep(fixture_dir / "diagram_analysis.json", DIAGRAM_ANALYSIS_JSON),

        CopyStep(DIAGRAM_ANALYSIS_JSON, DIAGRAM_ANALYSIS_COPY_JSON),

        # Part shapes come before the scene layout, which uses their sizes and
        # roles (top/leg/rail) to place parts where they actually attach.
        [sys.executable, "v2/agents/part_shape_extractor_agent.py"],

        [sys.executable, "v2/rendering/scene_layout_engine.py"],

        CopyStep(SCENE_LAYOUT_JSON, SCENE_LAYOUT_COPY_JSON),

        [sys.executable, "v2/builders/proxy_geometry_builder.py"],

        [sys.executable, "v2/rendering/blender_builder_v3.py"],
    ]
    if not render:
        return steps
    return steps + [
        # --python-exit-code makes an exception in the generated script fail
        # the stage instead of exiting 0.
        [BLENDER_EXE, "--background", "--python-exit-code", "1", "--python", str(BLENDER_V3_SCRIPT)],

        [sys.executable, "v2/rendering/render_video.py", "--title", product_title(fixture_dir)],
    ]


class PipelineStepError(RuntimeError):
    pass


def say(text: str, log: Optional[TextIO]) -> None:
    print(text, flush=True)
    if log:
        log.write(text + "\n")


def run_quiet(step: List[str], log: TextIO) -> int:
    """Run a stage, writing all its output to the log and echoing all but noise."""
    process = subprocess.Popen(
        step,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    frames = bars = 0
    for line in process.stdout:
        log.write(line)
        if FRAME_SAVED.search(line):
            frames += 1
        elif PROGRESS_BAR.search(line):
            bars += 1
        else:
            print(line, end="", flush=True)
    process.wait()

    hidden = [f"{frames} frame 'Saved:' lines"] if frames else []
    hidden += [f"{bars} progress-bar lines"] if bars else []
    if hidden:
        print(f"({' and '.join(hidden)} only in {LOG_PATH})", flush=True)
    return process.returncode


def run_command(step: Step, log: Optional[TextIO] = None) -> None:
    say("\n" + "=" * 80, log)
    say("RUNNING: " + (str(step) if isinstance(step, CopyStep) else " ".join(step)), log)
    say("=" * 80, log)

    if isinstance(step, CopyStep):
        if not step.source.exists():
            raise PipelineStepError(f"{step} failed: {step.source} does not exist.")
        step.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(step.source, step.destination)
        return

    if step[0] == BLENDER_EXE and not Path(BLENDER_EXE).exists():
        raise PipelineStepError(
            f"Blender not found at {BLENDER_EXE}. Install Blender or set BLENDER_EXE "
            "in .env to the full path of blender.exe."
        )

    returncode = run_quiet(step, log) if log else subprocess.run(step, shell=False).returncode

    if returncode != 0:
        raise PipelineStepError(
            f"Stage exited with code {returncode}: {' '.join(step)}. "
            "Its error is shown above; later stages were not run."
        )


def clear_old_outputs():
    ensure_project_dirs()

    for item in FRAMES_V3_DIR.glob("*.png"):
        item.unlink()

    if VIDEO_V3_PATH.exists():
        VIDEO_V3_PATH.unlink()

    for json_dir in (V2_JSON_DIR, V2_OUTPUT_DIR):
        if json_dir.exists():
            for item in json_dir.glob("*.json"):
                item.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("manual", help="Manual name under manuals/, or a folder holding its vision files.")
    parser.add_argument("--quiet", action="store_true",
                        help="Keep per-frame lines and progress bars out of the console; the log keeps everything.")
    parser.add_argument("--no-render", action="store_true",
                        help="Stop after writing the Blender script: no Blender, no video.")
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_project_dirs()

    manual_dir = Path(args.manual)
    if not manual_dir.is_dir():
        manual_dir = MANUALS_DIR / args.manual
    if not is_described(manual_dir):
        sys.exit(
            f"[PIPELINE FAILED] {manual_dir} has no {' / '.join(VISION_FILES)}. "
            f"Describe the manual first (in Claude Code: /describe-manual {manual_dir.name})."
        )
    name = manual_dir.name

    print("Starting MVP pipeline...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Manual: {manual_dir}")
    print(f"Frames output: {FRAMES_V3_DIR}")
    print(f"Video output: {VIDEO_V3_PATH}")

    clear_old_outputs()

    log = None
    if args.quiet:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        log = LOG_PATH.open("w", encoding="utf-8")

    try:
        for step in build_steps(manual_dir, render=not args.no_render):
            run_command(step, log)
    except PipelineStepError as e:
        print(f"\n[PIPELINE FAILED] {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if log:
            log.close()

    if args.no_render:
        print(f"\n[SUCCESS] Stages up to the Blender script complete: {BLENDER_V3_SCRIPT}")
        return

    kept = VIDEOS_DIR / f"{name}.mp4"
    shutil.copyfile(VIDEO_V3_PATH, kept)

    print("\n[SUCCESS] MVP pipeline complete")
    print("Video should be here:")
    print(VIDEO_V3_PATH.resolve())
    print(f"Kept a copy as {kept.resolve()}")


if __name__ == "__main__":
    main()
