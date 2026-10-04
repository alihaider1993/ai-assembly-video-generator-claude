"""Helpers for describing a manual's pages as the pipeline's vision results:
manuals/<name>/page_states.json and diagram_analysis.json.

Each manual has a describe.py (written by reading its page images) that lists
the pages with part(), fastener(), tool(), action(), page() and diagram(),
then calls write_description(). Everything goes through vision_schema.py, so
the files have exactly the schema the pipeline expects.
"""
import copy
import json
from pathlib import Path

from vision_schema import validate_diagram_analysis, validate_page_state


def part(label, name, desc, shape, material, qty, features=(), pos="center", size=None, tilt=0.0, profile=None):
    """size: (width x, depth y, height z) in mm as fitted, estimated from the
    drawings when the manual prints none. tilt: degrees the fitted part
    leans back (a reclined chair back; a seat sloping down to the back).
    profile: a part's outline in its side view (plane "side": y forward
    to back, z up) or front view (plane "front": x, z), as a path of mm
    points traced with a strip "thickness" mm wide: bentwood frames,
    curved rails, armrests."""
    entry = {
        "part_uid": "", "manual_label": label, "name": name,
        "visual_description": desc, "shape_family": shape,
        "material_hint": material, "quantity_visible": qty,
        "connection_features": [
            {"feature_type": f, "count": c, "location_hint": loc} for f, c, loc in features
        ],
        "page_position": pos,
    }
    if size:
        entry["size_mm"] = list(size)
    if tilt:
        entry["tilt_deg"] = tilt
    if profile:
        entry["profile"] = profile
    return entry


def fastener(label, name, shape, qty):
    return {"fastener_uid": "", "manual_label": label, "name": name,
            "shape_family": shape, "quantity_visible": qty}


def tool(name):
    return {"tool_uid": "", "name": name}


def action(kind, moving, target, fast, tool_ref, direction, evidence):
    return {"action_uid": "", "action_type": kind, "moving_part_ref": moving,
            "target_part_ref": target, "fastener_ref": fast, "tool_ref": tool_ref,
            "direction_hint": direction, "visual_evidence": evidence}


def page(n, ptype, parts=(), fasteners=(), tools=(), actions=(), final="", unc=()):
    return copy.deepcopy({"page_number": n, "page_type": ptype, "visible_parts": list(parts),
                          "visible_fasteners": list(fasteners), "visible_tools": list(tools),
                          "observed_actions": list(actions), "final_visible_structure": final,
                          "uncertainties": list(unc)})


def diagram(dtype, desc, region, labels=(), parts=True, fast=False, tools=False,
            arrows=False, action_="none", complexity="medium", conf=0.8):
    x0, y0, x1, y1 = region
    return {"diagram_uid": "", "diagram_type": dtype, "description": desc,
            "page_region": {"x_min": x0, "y_min": y0, "x_max": x1, "y_max": y1},
            "contains_parts": parts, "contains_fasteners": fast, "contains_tools": tools,
            "contains_arrows": arrows, "contains_labels": bool(labels),
            "visible_labels": list(labels), "likely_action": action_,
            "visual_complexity": complexity, "confidence": conf}


def write_description(out: Path, pages, diagrams) -> None:
    """Validate the pages and write page_states.json and diagram_analysis.json
    into `out`. `diagrams` maps page number -> (page_type, diagrams, uncertainties)."""
    out.mkdir(parents=True, exist_ok=True)
    states = [validate_page_state(p)[0] for p in pages]
    (out / "page_states.json").write_text(json.dumps(states, indent=2) + "\n", encoding="utf-8")

    analyses = []
    for n, (ptype, items, unc) in diagrams.items():
        data = {"page_number": n, "page_type": ptype, "diagrams": items,
                "primary_assembly_diagram": "", "warnings": [], "uncertainties": unc}
        analyses.append(validate_diagram_analysis(data, n))
    (out / "diagram_analysis.json").write_text(json.dumps(analyses, indent=2) + "\n", encoding="utf-8")

    for s in states:
        print(s["page_number"], s["page_type"], len(s["visible_parts"]),
              len(s["observed_actions"]), s["uncertainties"][-1:])
