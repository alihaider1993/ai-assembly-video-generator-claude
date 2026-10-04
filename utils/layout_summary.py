"""Print the last pipeline run's layout and motion plan as one short table,
instead of reading scene_layout.json, motion_plan.json and part_shapes.json
(50-80 KB each).

Usage (from the repo root, after the pipeline has run at least up to
scene_layout_engine.py):
    python utils/layout_summary.py

Shows the layout mode, finale, every step, and every object's role, size,
start and final position. Warnings are always printed in full. Open the JSON
files themselves when something here looks wrong.
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import MOTION_PLAN_JSON, PART_SHAPES_JSON, SCENE_LAYOUT_JSON


def load(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"{path} does not exist. Run the pipeline up to scene_layout_engine.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def xyz(values) -> str:
    """Metres to millimetres, rounded: enough to check placement."""
    return "(" + ", ".join(f"{v * 1000:.0f}" for v in values) + ")" if values else "-"


def print_warnings(source: str, warnings: list) -> None:
    for warning in warnings:
        print(f"WARNING [{source}]: {warning}")


def main():
    layout = load(SCENE_LAYOUT_JSON)
    plan = load(MOTION_PLAN_JSON)
    shapes = {p["part_uid"]: p for p in load(PART_SHAPES_JSON).get("parts", [])} if PART_SHAPES_JSON.exists() else {}

    debug = layout.get("debug", {})
    render = layout.get("render", {})
    print(f"Layout mode: {debug.get('layout_mode', '?')}   finale: {json.dumps(layout.get('finale'))}")
    print(f"Frames: {render.get('total_frames', plan.get('total_frames'))} at {render.get('fps', plan.get('fps'))} fps   "
          f"camera: {json.dumps(layout.get('camera'))}")
    print("Debug: " + ", ".join(f"{k}={v}" for k, v in debug.items() if not isinstance(v, list)))
    print_warnings("scene_layout", layout.get("warnings", []))
    print_warnings("motion_plan", plan.get("warnings", []))

    print(f"\nSteps ({len(plan.get('steps', []))}):")
    for step in plan.get("steps", []):
        print(f"  {step['step_uid']} f{step.get('start_frame')}-{step.get('end_frame')} p{step.get('source_page')} "
              f"{step.get('action_type')}/{step.get('motion_style')}: "
              f"{','.join(step.get('moving_nodes', []))} -> {','.join(step.get('target_nodes', []))}  "
              f"\"{step.get('title', '')}\"")

    objects = layout.get("scene_objects", [])
    print(f"\nObjects ({len(objects)}), positions in mm:")
    print("  uid | type | name | role | size | start -> final | rotation | first step | flags")
    for obj in objects:
        shape = shapes.get(obj["node_uid"], {})
        size = "x".join(f"{d * 1000:.0f}" for d in shape.get("dimensions", [])) or "-"
        flags = [f for f, on in (("moving", obj.get("is_moving")), ("target", obj.get("is_target")),
                                 ("hidden", obj.get("visible") is False)) if on]
        if obj.get("parent"):
            flags.append(f"parent={obj['parent']}")
        print(f"  {obj['node_uid']} | {obj.get('node_type')} | {obj.get('name')} | {shape.get('role', '-')} | "
              f"{size} ({shape.get('dims_source', '-')}) | {xyz(obj.get('start_position'))} -> "
              f"{xyz(obj.get('final_position'))} | {obj.get('rotation')} | {obj.get('first_motion_step', '-')} | "
              f"{' '.join(flags)}")


if __name__ == "__main__":
    main()
