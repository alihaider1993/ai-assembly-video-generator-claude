import subprocess
import sys
import time
import zipfile
from pathlib import Path

import streamlit as st

from config import (
    FRAMES_V3_DIR,
    MANUALS_DIR,
    OUTPUTS_DIR,
    VIDEOS_DIR,
    V2_JSON_DIR,
    V2_OUTPUT_DIR,
    ensure_project_dirs,
    is_described,
)
from utils.pdf_to_images import add_manual, manual_name


st.set_page_config(
    page_title="AI Assembly Video Generator",
    page_icon="🛠️",
    layout="wide",
)


PIPELINE_STEPS = [
    "Load page descriptions",
    "Assembly actions",
    "Assembly graph",
    "Motion plan",
    "Part shapes",
    "Scene layout",
    "Blender render",
    "MP4 video",
    "Complete",
]


def render_pipeline_status(active_index: int):
    for row_start in (0, 5):
        row = PIPELINE_STEPS[row_start:row_start + 5]
        cols = st.columns(5)

        for offset, step in enumerate(row):
            i = row_start + offset
            with cols[offset]:
                if i < active_index:
                    st.success(f"[DONE]\n\n{step}")
                elif i == active_index:
                    st.warning(f"[RUNNING]\n\n{step}")
                else:
                    st.info(f"[WAITING]\n\n{step}")


def detect_step(line: str, current_step: int) -> int:
    # Matches the "RUNNING: ..." line run_mvp_pipeline.py prints before each stage.
    text = line.lower()

    if "assembly_action_extractor" in text or "state_difference_engine" in text:
        return max(current_step, 1)
    if "universal_graph_engine" in text or "object_identity_tracker" in text:
        return max(current_step, 2)
    if "motion_planner" in text:
        return max(current_step, 3)
    if "part_shape_extractor" in text:
        return max(current_step, 4)
    if "scene_layout_engine" in text:
        return max(current_step, 5)
    if "blender" in text or "saved:" in text:
        return max(current_step, 6)
    if "render_video" in text or "video created" in text:
        return max(current_step, 7)
    if "mvp pipeline complete" in text:
        return 8

    return current_step


def run_live_command(cmd, log_box, progress_bar, status_area):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    logs = []
    current_step = 0
    frame_count = 0

    for line in process.stdout:
        line = line.rstrip()
        logs.append(line)

        current_step = detect_step(line, current_step)

        if "Saved:" in line and "frame_" in line:
            frame_count += 1
            progress_bar.progress(
                min(current_step / (len(PIPELINE_STEPS) - 1), 1.0),
                text=f"Rendering Blender frames... {frame_count}",
            )
        else:
            progress_bar.progress(
                min(current_step / (len(PIPELINE_STEPS) - 1), 1.0),
                text=f"Current step: {PIPELINE_STEPS[current_step]}",
            )

        with status_area.container():
            render_pipeline_status(current_step)

        log_box.code("\n".join(logs[-100:]))

    if process.wait() != 0:
        # Stages print "[FATAL] ..." / "[PIPELINE FAILED] ..." with the actual
        # cause (e.g. Blender not found); show that instead of just the command.
        reasons = [
            line for line in logs
            if line.startswith(("[FATAL]", "[PIPELINE FAILED]"))
        ]
        details = "\n\n".join(reasons) if reasons else "\n".join(logs[-15:])
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n\n{details}")


def run_pipeline(name: str):
    status_area = st.empty()
    progress_bar = st.progress(0, text="Starting pipeline...")

    with st.expander("Live pipeline logs", expanded=True):
        log_box = st.empty()

    start_time = time.time()

    with status_area.container():
        render_pipeline_status(0)

    run_live_command(
        [sys.executable, "-u", "v2/run_mvp_pipeline.py", name],
        log_box,
        progress_bar,
        status_area,
    )

    elapsed = time.time() - start_time
    progress_bar.progress(1.0, text=f"Complete in {elapsed:.1f} seconds")

    with status_area.container():
        render_pipeline_status(len(PIPELINE_STEPS) - 1)


def generated_json_files():
    # v2/output/ holds copies of diagram_analysis.json and scene_layout.json;
    # list each file name once.
    files = list(V2_JSON_DIR.glob("*.json"))
    names = {f.name for f in files}
    return files + [f for f in V2_OUTPUT_DIR.glob("*.json") if f.name not in names]


def create_json_zip() -> Path:
    zip_path = OUTPUTS_DIR / "generated_json_files.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in generated_json_files():
            zipf.write(file, arcname=file.name)

    return zip_path


def show_json_downloads():
    st.subheader("Generated JSON outputs")
    st.caption("From the last run.")

    json_files = generated_json_files()

    if not json_files:
        st.info("No JSON files yet. Generate a video to create them.")
        return

    with open(create_json_zip(), "rb") as f:
        st.download_button(
            "Download all JSON files",
            data=f,
            file_name="generated_json_files.zip",
            mime="application/zip",
        )

    with st.expander("View individual JSON files"):
        for file in json_files:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"`{file}`")

            with col2:
                with open(file, "rb") as f:
                    st.download_button(
                        "Download",
                        data=f,
                        file_name=file.name,
                        mime="application/json",
                        key=str(file),
                    )


def show_video(name: str):
    video = VIDEOS_DIR / f"{name}.mp4"

    if not video.exists():
        st.info("No video for this manual yet. Select Generate assembly video to make one.")
        return

    st.video(str(video))

    with open(video, "rb") as f:
        st.download_button(
            "Download MP4",
            data=f,
            file_name=video.name,
            mime="video/mp4",
            use_container_width=True,
        )


def add_manual_form():
    st.subheader("1. Add a manual")

    uploaded = st.file_uploader("Instruction manual PDF", type=["pdf"])
    if not uploaded:
        return

    name = st.text_input("Manual name", value=manual_name(Path(uploaded.name)))
    if st.button("Add manual"):
        manual_dir = MANUALS_DIR / manual_name(Path(name or uploaded.name))
        manual_dir.mkdir(parents=True, exist_ok=True)
        pdf = manual_dir / "manual.pdf"
        pdf.write_bytes(uploaded.getvalue())
        add_manual(pdf, manual_dir.name)
        pages = len(list((manual_dir / "pages").glob("page_*.png")))
        st.success(f"Added {manual_dir.name} ({pages} pages).")


def list_manuals():
    return sorted(d.name for d in MANUALS_DIR.iterdir() if d.is_dir()) if MANUALS_DIR.exists() else []


def show_frames():
    frames = sorted(FRAMES_V3_DIR.glob("*.png"))

    if not frames:
        st.info("Frames from the last run will appear here.")
        return

    st.subheader(f"Frame preview ({len(frames)} frames, last run)")

    for col, frame, label in zip(
        st.columns(3),
        [frames[0], frames[len(frames) // 2], frames[-1]],
        ["First frame", "Middle frame", "Final frame"],
    ):
        with col:
            st.image(str(frame), caption=label)


def main():
    ensure_project_dirs()

    st.title("🛠️ AI Assembly Video Generator")
    st.caption(
        "Turns an assembly manual into an animated video: assembly graph, "
        "motion plan, 3D layout and a Blender render."
    )

    st.markdown("---")
    add_manual_form()

    st.markdown("---")
    st.subheader("2. Make the video")

    manuals = list_manuals()
    if not manuals:
        st.info("No manuals yet. Add one above.")
        return

    name = st.selectbox("Manual", options=manuals)
    manual_dir = MANUALS_DIR / name

    if not is_described(manual_dir):
        st.warning(
            f"This manual's pages haven't been described yet. In Claude Code, run "
            f"`/describe-manual {name}`, then come back and generate the video."
        )
    elif st.button("Generate assembly video", type="primary", use_container_width=True):
        try:
            run_pipeline(name)
            st.success("Assembly video generated.")
        except Exception as e:
            st.error(str(e))
            return

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Video", "Frame preview", "JSON outputs"])

    with tab1:
        show_video(name)

    with tab2:
        show_frames()

    with tab3:
        show_json_downloads()


if __name__ == "__main__":
    main()
