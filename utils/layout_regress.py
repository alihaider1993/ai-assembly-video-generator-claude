"""Layout regression check: does a code change move parts in other manuals?

Each described manual has a snapshot in v2/tests/layout_snapshots/<name>.json:
its motion steps (what moves onto what), the finale, and every object's final
position, rotation and scale. `check` re-runs the pipeline without rendering
and compares; a part that moved more than TOLERANCE_M (or a changed step) is a
failure. When a change is meant to move parts, look at the new layout (render
it), then `update` the snapshot and commit it with the change.

Usage (from the repo root):
    python utils/layout_regress.py check [NAME ...]           # all described manuals by default
    python utils/layout_regress.py check NAME --no-run        # compare the last run's output (CI)
    python utils/layout_regress.py update [NAME ...]          # re-run and save new snapshots

Runs manuals one at a time; output paths are fixed, so don't start another
pipeline run while it works.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import MANUALS_DIR, MOTION_PLAN_JSON, SCENE_LAYOUT_JSON, is_described

SNAPSHOT_DIR = PROJECT_ROOT / "v2" / "tests" / "layout_snapshots"
# Small enough to catch a misplaced part, large enough for float differences
# between machines.
TOLERANCE_M = 0.002
TOLERANCE_DEG = 0.5
TOLERANCE_SCALE = 0.005


def described_manuals():
    return sorted(p.name for p in MANUALS_DIR.iterdir() if p.is_dir() and is_described(p))


def run_pipeline(name: str) -> bool:
    result = subprocess.run([sys.executable, "v2/run_mvp_pipeline.py", name, "--no-render", "--quiet"],
                            cwd=PROJECT_ROOT, capture_output=True, text=True)
    if result.returncode:
        print(f"{name}: PIPELINE FAILED\n{result.stdout[-1500:]}{result.stderr[-1500:]}")
    return result.returncode == 0


def snapshot_from_outputs() -> dict:
    plan = json.loads(Path(PROJECT_ROOT / MOTION_PLAN_JSON).read_text(encoding="utf-8"))
    layout = json.loads(Path(PROJECT_ROOT / SCENE_LAYOUT_JSON).read_text(encoding="utf-8"))
    r = lambda v: [round(float(x), 4) + 0.0 for x in v] if isinstance(v, list) else v
    return {
        "finale": layout.get("finale") or {},
        "steps": [[sorted(s.get("moving_nodes", [])), sorted(s.get("target_nodes", []))] for s in plan.get("steps", [])],
        "objects": {o["node_uid"]: {"pos": r(o.get("final_position")), "rot": r(o.get("rotation")), "scale": r(o.get("scale"))}
                    for o in layout.get("scene_objects", [])},
    }


def differences(old: dict, new: dict) -> list:
    out = []
    if old["steps"] != new["steps"]:
        out.append(f"motion steps changed ({len(old['steps'])} -> {len(new['steps'])})")
    if bool(old["finale"]) != bool(new["finale"]):
        out.append(f"finale changed: {old['finale'] or 'none'} -> {new['finale'] or 'none'}")
    for uid in sorted(set(old["objects"]) | set(new["objects"])):
        a, b = old["objects"].get(uid), new["objects"].get(uid)
        if a is None or b is None:
            out.append(f"{uid} {'added' if a is None else 'removed'}")
            continue
        for key, tol, unit, k in (("pos", TOLERANCE_M, "mm", 1000), ("rot", TOLERANCE_DEG, "deg", 1), ("scale", TOLERANCE_SCALE, "", 1)):
            va, vb = a.get(key) or [], b.get(key) or []
            if len(va) != len(vb) or any(abs(x - y) > tol for x, y in zip(va, vb)):
                fmt = lambda v: "(" + ", ".join(f"{x * k:.0f}" if k > 1 else f"{x:g}" for x in v) + ")"
                out.append(f"{uid} {key} {fmt(va)} -> {fmt(vb)} {unit}".rstrip())
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=["check", "update"])
    parser.add_argument("names", nargs="*")
    parser.add_argument("--no-run", action="store_true", help="use the last pipeline run's output (one manual)")
    args = parser.parse_args()
    names = args.names or described_manuals()
    if args.no_run and len(names) != 1:
        parser.error("--no-run compares one manual: the one the pipeline last ran")

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    failed = []
    for name in names:
        if not args.no_run and not run_pipeline(name):
            failed.append(name)
            continue
        new = snapshot_from_outputs()
        path = SNAPSHOT_DIR / f"{name}.json"
        if args.mode == "update":
            path.write_text(json.dumps(new, indent=1, sort_keys=True), encoding="utf-8")
            print(f"{name}: snapshot saved")
            continue
        if not path.exists():
            print(f"{name}: no snapshot yet (run: python utils/layout_regress.py update {name})")
            failed.append(name)
            continue
        diffs = differences(json.loads(path.read_text(encoding="utf-8")), new)
        if diffs:
            failed.append(name)
            print(f"{name}: {len(diffs)} change(s)")
            for line in diffs[:25]:
                print(f"  {line}")
            if len(diffs) > 25:
                print(f"  ... and {len(diffs) - 25} more")
        else:
            print(f"{name}: unchanged")

    if args.mode == "check" and failed:
        print(f"\nChanged or failed: {', '.join(failed)}. If intended, review the layout, then run "
              f"'python utils/layout_regress.py update {' '.join(failed)}' and commit the snapshots.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
