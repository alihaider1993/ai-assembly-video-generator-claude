import json
from pathlib import Path

# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

# ==========================================================
# MANUALS
# ==========================================================

# One folder per manual: manuals/<name>/ holds manual.pdf and pages/ (both
# git-ignored), describe.py (the page-by-page description, written by
# reading the pages) and the two vision files it generates, which the
# pipeline starts from.
MANUALS_DIR = PROJECT_ROOT / "manuals"

VISION_FILES = ("page_states.json", "diagram_analysis.json")


def is_described(manual_dir: Path) -> bool:
    return all((manual_dir / name).exists() for name in VISION_FILES)


def product_title(manual_dir: Path) -> str:
    """The product's name for the video title: product.json's "title" (set
    by describe.py), else the folder name ("brimnes_wardrobe" -> "Brimnes Wardrobe")."""
    try:
        title = json.loads((manual_dir / "product.json").read_text(encoding="utf-8")).get("title", "")
    except (OSError, ValueError):
        title = ""
    return title.strip() or manual_dir.name.replace("_", " ").replace("-", " ").title()


# ==========================================================
# OUTPUTS
# ==========================================================

OUTPUTS_DIR = PROJECT_ROOT / "outputs"

FRAMES_V3_DIR = OUTPUTS_DIR / "frames_v3"

VIDEO_V3_PATH = OUTPUTS_DIR / "assembly_animation_v3.mp4"

# Each finished run is also kept here as <product>.mp4.
VIDEOS_DIR = OUTPUTS_DIR / "videos"

# ==========================================================
# WEBSITE
# ==========================================================

# Finished videos shown on the website, picked by hand with
# utils/showcase.py. Unlike outputs/, this folder is committed.
SHOWCASE_DIR = PROJECT_ROOT / "showcase"

SHOWCASE_JSON = SHOWCASE_DIR / "showcase.json"

# Limits on manuals uploaded through the website.
MAX_UPLOAD_PAGES = 10

MAX_UPLOAD_MB = 2

# Uploads made on the website (web/server.py) and their videos, deleted
# JOB_KEEP_SECONDS after they finish. Each upload asks Gemini once, so the
# daily caps keep the site inside the free tier.
JOBS_DIR = OUTPUTS_DIR / "jobs"

JOB_KEEP_SECONDS = 60 * 60

MAX_QUEUED_JOBS = 5

DAILY_JOB_LIMIT = 20

DAILY_JOBS_PER_VISITOR = 3

# ==========================================================
# BLENDER
# ==========================================================

BLENDER_DIR = PROJECT_ROOT / "blender"

BLENDER_GENERATED_DIR = BLENDER_DIR / "generated"

BLENDER_V3_SCRIPT = BLENDER_GENERATED_DIR / "v3_generated_blender_scene.py"

# ==========================================================
# V2 OUTPUTS
# ==========================================================

V2_DIR = PROJECT_ROOT / "v2"

V2_JSON_DIR = V2_DIR / "outputs" / "json"

V2_OUTPUT_DIR = V2_DIR / "output"

# JSON Files

PAGE_STATES_JSON = V2_JSON_DIR / "page_states.json"

ASSEMBLY_DELTAS_JSON = V2_JSON_DIR / "assembly_deltas.json"

ASSEMBLY_ACTIONS_JSON = V2_JSON_DIR / "assembly_actions.json"

UNIVERSAL_GRAPH_JSON = V2_JSON_DIR / "universal_assembly_graph.json"

MOTION_PLAN_JSON = V2_JSON_DIR / "motion_plan.json"

SCENE_LAYOUT_JSON = V2_JSON_DIR / "scene_layout.json"

DIAGRAM_ANALYSIS_JSON = V2_JSON_DIR / "diagram_analysis.json"

GEOMETRY_SPEC_JSON = V2_JSON_DIR / "geometry_spec.json"

# Frame timing and captions of the rendered video (blender_builder_v3.py
# writes it, render_video.py draws the captions from it)
RENDER_TIMELINE_JSON = V2_JSON_DIR / "render_timeline.json"

# Intermediate Files

PART_SHAPES_JSON = V2_OUTPUT_DIR / "part_shapes.json"

PROXY_GEOMETRY_JSON = V2_OUTPUT_DIR / "proxy_geometry.json"

DIAGRAM_ANALYSIS_COPY_JSON = V2_OUTPUT_DIR / "diagram_analysis.json"

SCENE_LAYOUT_COPY_JSON = V2_OUTPUT_DIR / "scene_layout.json"

# ==========================================================
# CREATE DIRECTORIES
# ==========================================================

def ensure_project_dirs():

    directories = [

        MANUALS_DIR,

        OUTPUTS_DIR,

        FRAMES_V3_DIR,

        VIDEOS_DIR,

        BLENDER_GENERATED_DIR,

        V2_JSON_DIR,

        V2_OUTPUT_DIR,

    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)