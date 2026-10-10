"""Layout regression check: does a code change move parts in other manuals?

Each described manual has a snapshot in v2/tests/layout_snapshots/<name>.json:
its motion steps (what moves onto what), the finale, every object's final
position, rotation and scale, and the sanity issues it has (a part below the
floor, two panels passing through each other, a moved part ending away from
what it is joined to). `check` re-runs the pipeline without rendering and
compares; a part that moved more than TOLERANCE_M, a changed step, or a NEW
issue is a failure (issues already in the snapshot are known flaws). When a
change is meant to move parts, look at the new layout (render it), then
`update` the snapshot and commit it with the change.

Usage (from the repo root):
    python utils/layout_regress.py check [NAME ...]           # all described manuals by default
    python utils/layout_regress.py check NAME --no-run        # compare the last run's output (CI)
    python utils/layout_regress.py update [NAME ...]          # re-run and save new snapshots

Runs manuals one at a time; output paths are fixed, so don't start another
pipeline run while it works.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import MANUALS_DIR, UNIVERSAL_GRAPH_JSON, MOTION_PLAN_JSON, PROXY_GEOMETRY_JSON, SCENE_LAYOUT_JSON, is_described

SNAPSHOT_DIR = PROJECT_ROOT / "v2" / "tests" / "layout_snapshots"
# Small enough to catch a misplaced part, large enough for float differences
# between machines.
TOLERANCE_M = 0.002
TOLERANCE_DEG = 0.5
TOLERANCE_SCALE = 0.005
# Sanity checks: how far under the floor counts, which parts are large
# panels (second-largest side), how much of the smaller one two of them may
# share, and how far a moved part may end from what it is joined to.
FLOOR_SLACK_M = 0.005
LARGE_PANEL_M = 0.2
OVERLAP_SHARE = 0.2
TOUCH_SLACK_M = 0.03


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
        "issues": issues_in_outputs(),
        "objects": {o["node_uid"]: {"pos": r(o.get("final_position")), "rot": r(o.get("rotation")), "scale": r(o.get("scale"))}
                    for o in layout.get("scene_objects", [])},
    }


def part_boxes() -> dict:
    """uid -> (lo, hi) world box of every placed part, from the last run's
    layout and proxy geometry."""
    sys.path.insert(0, str(PROJECT_ROOT / "v2" / "rendering"))
    from general_layout import matmul, rotation_matrix

    layout = json.loads(Path(PROJECT_ROOT / SCENE_LAYOUT_JSON).read_text(encoding="utf-8"))
    proxies = json.loads(Path(PROJECT_ROOT / PROXY_GEOMETRY_JSON).read_text(encoding="utf-8")).get("objects", [])
    proxy = {p["part_uid"]: p for p in proxies}
    boxes = {}
    for o in layout.get("scene_objects", []):
        uid = o["node_uid"]
        if o.get("node_type") != "part" or uid not in proxy:
            continue
        p = proxy[uid]
        m = matmul(rotation_matrix(o.get("rotation") or [0, 0, 0]), rotation_matrix(p.get("rotation") or [0, 0, 0]))
        half = [d * s / 2 for d, s in zip(p["dimensions"], o.get("scale") or [1, 1, 1])]
        ext = [sum(abs(m[i][j]) * half[j] for j in range(3)) for i in range(3)]
        c = o.get("final_position")
        boxes[uid] = ([c[i] - ext[i] for i in range(3)], [c[i] + ext[i] for i in range(3)])
    return boxes


def issues_in_outputs() -> list:
    """Plain facts every finished piece should satisfy, checked on the last
    run: nothing below the floor; no two large panels passing through each
    other; every part moved in a step ends touching a part it was joined to."""
    boxes = part_boxes()
    out = []
    for uid, (lo, hi) in sorted(boxes.items()):
        if lo[2] < -FLOOR_SLACK_M:
            out.append(f"{uid} below the floor ({lo[2] * 1000:.0f} mm)")

    def size(b):
        return [b[1][i] - b[0][i] for i in range(3)]

    large = [u for u, b in boxes.items() if sorted(size(b))[1] >= LARGE_PANEL_M]
    for i, a in enumerate(sorted(large)):
        for b in sorted(large)[i + 1:]:
            (alo, ahi), (blo, bhi) = boxes[a], boxes[b]
            overlap = [min(ahi[k], bhi[k]) - max(alo[k], blo[k]) for k in range(3)]
            if min(overlap) <= 0:
                continue
            vol = overlap[0] * overlap[1] * overlap[2]
            smaller = min(max(1e-9, sz[0] * sz[1] * sz[2]) for sz in (size(boxes[a]), size(boxes[b])))
            if vol > OVERLAP_SHARE * smaller:
                out.append(f"{a} and {b} pass through each other")

    # A copy may be joined to a different copy than the one its step names
    # (left runners and the left panel), so any part it is joined to counts.
    graph = json.loads(Path(PROJECT_ROOT / UNIVERSAL_GRAPH_JSON).read_text(encoding="utf-8"))
    joined = {}
    for c in graph.get("connections", []):
        a, b = c.get("from_node_ref", ""), c.get("to_node_ref", "")
        joined.setdefault(a, set()).add(b)
        joined.setdefault(b, set()).add(a)
    plan = json.loads(Path(PROJECT_ROOT / MOTION_PLAN_JSON).read_text(encoding="utf-8"))
    for step in plan.get("steps", []):
        named = [t for t in step.get("target_nodes", []) if t in boxes]
        for uid in step.get("moving_nodes", []):
            targets = sorted(set(named) | {t for t in joined.get(uid, ()) if t in boxes})
            if uid not in boxes or not targets:
                continue
            gaps = []
            for t in targets:
                (alo, ahi), (blo, bhi) = boxes[uid], boxes[t]
                gaps.append(max(max(blo[k] - ahi[k], alo[k] - bhi[k], 0.0) for k in range(3)))
            if min(gaps) > TOUCH_SLACK_M:
                out.append(f"{uid} ends {min(gaps) * 1000:.0f} mm from every part it is joined to")
    return sorted(set(out))


def differences(old: dict, new: dict) -> list:
    # Issues are matched without their figures, which may round differently
    # on another machine.
    bare = lambda text: re.sub(r"\(?-?\d+ mm\)?", "", text).strip()
    known = {bare(i) for i in old.get("issues", [])}
    out = [f"new issue: {i}" for i in new.get("issues", []) if bare(i) not in known]
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
